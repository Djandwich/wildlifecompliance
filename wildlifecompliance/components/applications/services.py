import sys
import abc
import requests
import logging

from decimal import Decimal

from wildlifecompliance import settings

from ledger.checkout.utils import calculate_excl_gst

from wildlifecompliance.components.licences.models import (
    LicencePurpose,
    LicenceSpecies,
)

from wildlifecompliance.components.applications.models import (
    Application,
    ApplicationSelectedActivity,
    ApplicationSelectedActivityPurpose,
    ApplicationFormDataRecord,
    ApplicationStandardCondition,
    ApplicationCondition,
    LicenceActivity,
)

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.DEBUG)


class ApplicationService(object):
    """
    Services available for a Licence Application.
    """

    def __init__(self):
        pass

    @staticmethod
    def get_licence_species(species_list):
        """
        Gets species details.
        """
        requested_species = []
        for specie in species_list:
            details = []
            details = LicenceSpecies.objects.values('data').get(
                specie_id=specie)
            requested_species.append(details['data'])

        return requested_species

    @staticmethod
    def verify_licence_species():
        """
        Verifies species name identifier is current with the TSC database.
        """
        purposes = LicencePurpose.objects.all()
        species_list = []
        for purpose in purposes:
            species_list += purpose.get_group_species_list
            species_list += purpose.get_section_species_list

        tsc_service = TSCSpecieService(TSCSpecieCall())
        tsc_service.set_strategy(TSCSpecieXReferenceCall())

        species_set = set(species_list)     # create a list of unique values.
        species_list = (list(species_set))

        logger.info('ApplicationService: Verifying species.')

        for specie in species_list:
            tsc_service.search_taxon(specie)

        logger.info(
            'ApplicationService: Completed. Verified {0} species.'.format(
                len(species_list)))

    @staticmethod
    def verify_licence_specie_id(specie_id):
        """
        Verifies species name identifier is current with the TSC database.
        """
        tsc_service = TSCSpecieService(TSCSpecieCall())
        tsc_service.set_strategy(TSCSpecieXReferenceCall())
        logger.info('ApplicationService: Verifying species.')
        tsc_service.search_taxon(specie_id)
        logger.info('ApplicationService: Completed. Verified 1 specie.')

    @staticmethod
    def calculate_fees(application, data_source):
        """
        Calculates fees for Application and Licence. Application fee is
        calculated with the base fee in all instances to allow for adjustments
        made from form attributes. Previous attributes settings are not saved.
        Licence fees cannot be adjusted with form attributes.
        """
        # Get all fee adjustments made with checkboxes and radio buttons.
        checkbox = CheckboxAndRadioButtonVisitor(application, data_source)
        for_increase_fee_fields = IncreaseApplicationFeeFieldElement()
        for_increase_fee_fields.accept(checkbox)

        return for_increase_fee_fields.get_adjusted_fees()

    @staticmethod
    def get_product_lines(application):
        """
        Gets the application fee product lines to be charged through checkout.
        """
        return ApplicationFeePolicy.get_fee_product_lines_for(application)

    @staticmethod
    def process_form(
            request,
            application,
            form_data,
            action=ApplicationFormDataRecord.ACTION_TYPE_ASSIGN_VALUE):
        """
        Creates an application from Form attributes based on admin schema
        definition.
        """
        do_process_form(
            request,
            application,
            form_data,
            action=ApplicationFormDataRecord.ACTION_TYPE_ASSIGN_VALUE)

    @staticmethod
    def set_special_form_fields(application, form):
        """
        Set Special Form Field Attributes on an Application Form.
        """
        # Set form components to be visited.
        checkbox = CheckboxAndRadioButtonVisitor(application, form)
        text_area = TextAreaVisitor(application, form)

        # Set PromptInspection Fields for Checkbox and RadioButtons.
        for_inspection_fields = PromptInpsectionFieldElement()
        for_inspection_fields.accept(checkbox)

        # Set StandardCondition Fields for Checkbox and RadioButtons.
        for_condition_fields = StandardConditionFieldElement()
        for_condition_fields.accept(checkbox)

        # Set copy-to-licence Fields which allow for additional terminologies
        # to be dynamically added to the licence pdf.
        for_copy_to_licence_fields = CopyToLicenceFieldElement()
        for_copy_to_licence_fields.accept(text_area)

    @staticmethod
    def update_dynamic_attributes(application):
        """
        Updates application attributes based on admin schema definition.
        """
        do_update_dynamic_attributes(application)

    def __str__(self):
        return 'ApplicationService'


"""
NOTE: This section for objects relate to Application Form rendering.
"""


class ApplicationFormCompositor(object):
    """
    Declares an interface common to all supported Application Form algorithms.
    A context can use this interface to call a specific algorithm to act on
    a Special Field Element on a Application Form.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def do_algorithm(self, special_field_element):
        """
        Performs an algorithm applicable to a Special Field Element.
        """
        pass


class CheckboxAndRadioButtonCompositor(ApplicationFormCompositor):
    """
    A Class for objects which encapsulates an algorithm for formatting Checkbox
    and Radio buttons on an Application Form.
    """
    def __init__(self, application, data_source):
        self._application = application
        self._data_source = data_source
        self._children = set()

    def do_algorithm(self, special_field_element):
        self._field = special_field_element
        self.render()

    def render(self):

        for selected_activity in self._application.activities:

            self._field.reset(selected_activity)

            schema_fields = self._application.get_schema_fields_for_purposes(
                selected_activity.purposes.values_list('id', flat=True)
            )

            # Adjustments based on selected options (radios and checkboxes)
            adjusted_by_fields = {}
            for form_data_record in self._data_source:
                try:
                    # Retrieve dictionary of fields from a model instance
                    data_record = form_data_record.__dict__
                except AttributeError:
                    # If a raw form data (POST) is supplied, form_data_record
                    # is a key
                    data_record = self._data_source[form_data_record]

                schema_name = data_record['schema_name']
                if schema_name not in schema_fields:
                    continue
                schema_data = schema_fields[schema_name]
                licence_purpose = LicencePurpose.objects.get(
                    id=schema_data['licence_purpose_id']
                )
                if 'options' in schema_data:
                    for option in schema_data['options']:
                        # Only modifications if the current option is selected
                        if option['value'] != data_record['value']:
                            continue
                        self._field.parse_component(
                            component=option,
                            schema_name=schema_name,
                            adjusted_by_fields=adjusted_by_fields,
                            activity=selected_activity,
                            purpose=licence_purpose
                        )

                # If this is a checkbox - skip unchecked ones
                elif data_record['value'] == 'on':
                    self._field.parse_component(
                        component=schema_data,
                        schema_name=schema_name,
                        adjusted_by_fields=adjusted_by_fields,
                        activity=selected_activity,
                        purpose=licence_purpose
                    )


class TextAreaCompositor(ApplicationFormCompositor):
    """
    A Class for objects which encapsulates an algorithm for formatting Text
    Areas on an Application Form.
    """
    def __init__(self, application, data_source):
        self._application = application
        self._data_source = data_source
        self._children = set()

    def do_algorithm(self, special_field_element):
        self._field = special_field_element
        self.render()

    def render(self):
        for selected_activity in self._application.activities:

            self._field.reset(selected_activity)

            schema_fields = self._application.get_schema_fields_for_purposes(
                selected_activity.purposes.values_list('id', flat=True)
            )

            adjusted_by_fields = {}
            for form_data_record in self._data_source:
                try:
                    # Retrieve dictionary of fields from a model instance
                    data_record = form_data_record.__dict__
                except AttributeError:
                    # If a raw form data (POST) is supplied, form_data_record
                    # is a key
                    data_record = self._data_source[form_data_record]

                schema_name = data_record['schema_name']
                if schema_name not in schema_fields:
                    continue
                schema_data = schema_fields[schema_name]
                licence_purpose = LicencePurpose.objects.get(
                    id=schema_data['licence_purpose_id']
                )
                if schema_data['type'] == 'text_area':
                    self._field.parse_component(
                        component=schema_data,
                        schema_name=schema_name,
                        adjusted_by_fields=adjusted_by_fields,
                        activity=selected_activity,
                        purpose=licence_purpose
                    )


class ApplicationFormVisitor(object):
    """
    An Interface for Application Form component fields which can be visited.
    """
    __metaclass__ = abc.ABCMeta


class CheckboxAndRadioButtonVisitor(ApplicationFormVisitor):
    """
    An implementation of an operation declared by ApplicationFormVisitor to do
    an algorithm specific to Checkbox and Radio Buttons for a Form.

    NOTE: Local state is stored and will accumulate during the traversal of the
    Form.
    """
    def __init__(self, application, data_source):
        self._application = application
        self._data_source = data_source
        # Apply a traversal strategy.
        self._compositor = CheckboxAndRadioButtonCompositor(
            application,
            data_source
        )

    def visit_prompt_inspection_field(self, prompt_inspection_field):
        self._prompt_inspection_field = prompt_inspection_field
        self._compositor.do_algorithm(self._prompt_inspection_field)

    def visit_standard_condition_field(self, standard_condition_field):
        self._standard_condition_field = standard_condition_field
        self._compositor.do_algorithm(self._standard_condition_field)

    def visit_increase_application_fee_field(self, increase_fee_field):
        self._increase_application_fee_field = increase_fee_field
        self._compositor.do_algorithm(self._increase_application_fee_field)


class TextAreaVisitor(ApplicationFormVisitor):
    """
    An implementation of an operation declared by ApplicationFormVisitor to do
    an algorithm specific to Text Area on a Form.

    NOTE: Local state is stored and will accumulate during the traversal of the
    Form.
    """
    def __init__(self, application, data_source):
        self._application = application
        self._data_source = data_source
        # Apply a traversal strategy.
        self._compositor = TextAreaCompositor(application, data_source)

    def visit_copy_to_licence_field(self, copy_to_licence_field):
        self._copy_to_licence_field = copy_to_licence_field
        self._compositor.do_algorithm(self._copy_to_licence_field)


class SpecialFieldElement(object):
    """
    Special Field that defines an Accept operation that takes a
    ApplicationFormVisitor as an argument.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def accept(self, visitor):
        pass


class CopyToLicenceFieldElement(SpecialFieldElement):
    """
    An implementation of an SpecialFieldElement operation that takes a
    ApplicationFormVisitor as an argument.
    """
    _NAME = 'CopyToLicence'

    is_refreshing = False       # Flag indicating a page refresh.

    def accept(self, application_form_visitor):
        self._terms = {'terms': []}
        self._application = application_form_visitor._application
        self._data_source = application_form_visitor._data_source
        if not self._data_source:
            self.is_refreshing = True
        application_form_visitor.visit_copy_to_licence_field(self)

    def reset(self, licence_activity):
        """
        Reset the selected licence activity to have no CopyToLicenceFields.
        """
        if self.is_refreshing:
            # No user update with a page refesh.
            return

        if isinstance(licence_activity, ApplicationSelectedActivity):
            licence_activity.additional_licence_info = self._terms
            licence_activity.save()

    def parse_component(
            self,
            component,
            schema_name,
            adjusted_by_fields,
            activity,
            purpose):

        if self.is_refreshing:
            # No user update with a page refesh.
            return

        if set([self._NAME]).issubset(component):
            """
            Set the selected licence activity to have CopyToLicenceFields.
            """
            _header = {
                'header': component[self._NAME],
                'condition': component['condition'],
                'name': component['name']
                }
            activity.additional_licence_info['terms'].append(_header)
            activity.save()

    def __str__(self):
        return 'Field Element: {0}'.format(self._NAME)


class PromptInpsectionFieldElement(SpecialFieldElement):
    """
    An implementation of an SpecialFieldElement operation that takes a
    ApplicationFormVisitor as an argument.
    """
    _NAME = 'PromptInspection'

    is_refreshing = False       # Flag indicating a page refresh.

    def accept(self, application_form_visitor):
        self._application = application_form_visitor._application
        self._data_source = application_form_visitor._data_source
        if not self._data_source:
            self.is_refreshing = True
        application_form_visitor.visit_prompt_inspection_field(self)

    def reset(self, licence_activity):

        if self.is_refreshing:
            # No user update with a page refesh.
            return

        if isinstance(licence_activity, ApplicationSelectedActivity):
            licence_activity.is_inspection_required = False
            licence_activity.save()

    def parse_component(
            self,
            component,
            schema_name,
            adjusted_by_fields,
            activity,
            purpose):

        if self.is_refreshing:
            # No user update with a page refesh.
            return

        if set([self._NAME]).issubset(component):
            activity.is_inspection_required = True
            activity.save()

    def __str__(self):
        return 'Field Element: {0}'.format(self._NAME)


class StandardConditionFieldElement(SpecialFieldElement):
    """
    An implementation of an SpecialFieldElement operation that takes a
    ApplicationFormVisitor as an argument.
    """
    _NAME = 'StandardCondition'

    is_refreshing = False       # Flag indicating a page refresh.

    def accept(self, application_form_visitor):
        self._application = application_form_visitor._application
        self._data_source = application_form_visitor._data_source
        if not self._data_source:
            self.is_refreshing = True
        application_form_visitor.visit_standard_condition_field(self)

    def reset(self, licence_activity):
        """
        Reset the Selected Activity to have no Standard Condition created.

        NOTE: Standard Conditions created will need to be manually deleted
        by the officer when need to change so that it is audited.
        """
        if self.is_refreshing:
            # No user update with a page refesh.
            return

        if isinstance(licence_activity, ApplicationSelectedActivity):
            # Do not delete when previously added.
            pass

    def parse_component(
            self,
            component,
            schema_name,
            adjusted_by_fields,
            activity,
            purpose):

        if self.is_refreshing:
            # No user update with a page refesh.
            return

        if set([self._NAME]).issubset(component):
            """
            Set the Selected Activity to contain Standard Conditon.
            """
            condition = ApplicationStandardCondition.objects.filter(
                code=component[self._NAME],
                obsolete=False).first()
            if condition:
                ac, created = ApplicationCondition.objects.get_or_create(
                    standard_condition=condition,
                    is_rendered=True,
                    standard=True,
                    application=self._application)
                ac.licence_activity = LicenceActivity.objects.get(
                        id=activity.licence_activity_id)
                ac.licence_purpose = purpose
                ac.return_type = condition.return_type
                ac.save()

    def __str__(self):
        return 'Field Element: {0}'.format(self._NAME)


class IncreaseApplicationFeeFieldElement(SpecialFieldElement):
    """
    An implementation of an SpecialFieldElement operation that takes a
    ApplicationFormVisitor as an argument and dynamically updates any increased
    adjustments to the application fee for the Activity/Purpose.
    """
    NAME = 'IncreaseApplicationFee'

    fee_policy = None           # Policy applied to the fee update.
    dynamic_attributes = None   # Attributes on the Activity Purpose.
    additional_fee = 0          # Amount the Application Fee is increased by.
    is_updating = False         # Flag indicating if update or retrieval.
    is_refreshing = False       # Flag indicating a page refresh.

    def accept(self, application_form_visitor):
        self._app = application_form_visitor._application
        self._data_source = application_form_visitor._data_source
        # Add relevant Fee policy to impact the Increase Application Fee.
        self.fee_policy = ApplicationFeePolicy.get_fee_policy_for(self._app)
        if not self._data_source:  # No form data set fee from application fee.
            self.fee_policy.set_application_fee()
            self.is_refreshing = True
        self.dynamic_attributes = self.fee_policy.get_dynamic_attributes()

        application_form_visitor.visit_increase_application_fee_field(self)

    def set_updating(self, is_update):
        '''
        Sets the flag indicating that this visit is an update and not retrieve
        for estimate calculation.
        '''
        self.is_updating = is_update

    def reset(self, licence_activity):
        '''
        Reset the fees for the licence activity to it base fee amount.
        '''
        if self.is_refreshing:
            # No user update with a page refesh.
            return

        if isinstance(licence_activity, ApplicationSelectedActivity):
            self.dynamic_attributes[
                'activity_attributes'][licence_activity] = {
                    'fees': licence_activity.base_fees
                }
            # reset purpose adjusted fee amount.
            if self.is_updating:
                purposes = ApplicationSelectedActivityPurpose.objects.filter(
                    selected_activity=licence_activity,
                )
                for p in purposes:
                    p.adjusted_fee = 0
                    p.save()

                licence_activity.save()

    def parse_component(
            self,
            component,
            schema_name,
            adjusted_by_fields,
            activity,
            purpose):
        '''
        Aggregate adjusted fees for the Activity/Purpose.
        '''
        if self.is_refreshing:
            # No user update with a page refesh.
            return

        self.adjusted_fee = 0
        if set([self.NAME]).issubset(component):
            def increase_fee(fees, field, amount):
                fees[field] += amount
                fees[field] = fees[field] if fees[field] >= 0 else 0
                return True

            def adjusted_fee(amount):
                self.adjusted_fee += amount
                return True

            fee_modifier_keys = {
                'NoIncreaseLicenceFee': 'licence',
                self.NAME: 'application',
            }
            increase_limit_key = 'IncreaseTimesLimit'
            try:
                increase_count = adjusted_by_fields[schema_name]
            except KeyError:
                increase_count = adjusted_by_fields[schema_name] = 0

            if increase_limit_key in component:
                max_increases = int(component[increase_limit_key])
                if increase_count >= max_increases:
                    return

            adjustments_performed = sum(key in component and increase_fee(
                self.dynamic_attributes['fees'],
                field,
                component[key]
            ) and increase_fee(
                self.dynamic_attributes[
                    'activity_attributes'][activity]['fees'],
                field,
                component[key]
            ) and adjusted_fee(
                component[key]
            ) for key, field in fee_modifier_keys.items())

            if adjustments_performed:
                adjusted_by_fields[schema_name] += 1

            if self.is_updating and adjustments_performed:
                # update adjusted fee for the activity purpose.
                p = ApplicationSelectedActivityPurpose.objects.get_or_create(
                    purpose=purpose,
                    selected_activity=activity,
                )
                p[0].adjusted_fee = self.adjusted_fee
                p[0].save()

    def get_adjusted_fees(self):
        '''
        Gets the new dynamic attributes after the Increase Application Fee
        has been applied with the relevant fee policy.
        '''
        if self.is_refreshing:
            # don't calculate new fees for attributes.
            return self.dynamic_attributes['fees']

        self.fee_policy.set_dynamic_attributes(self.dynamic_attributes)

        return self.dynamic_attributes['fees']

    def set_adjusted_fees_for(self, activity):
        '''
        Sets the Increase Application Fee on the licence activity applying the
        relevant fee policy.
        '''
        if self.is_refreshing:
            # don't calculate new fees for attributes.
            return

        self.fee_policy.set_dynamic_attributes_for(activity)

    def get_dynamic_attributes(self):
        '''
        Gets the current dynamic attributes created by this Field Element.
        '''
        return self.dynamic_attributes

    def __str__(self):
        return 'Field Element: {0}'.format(self._NAME)


def do_process_form(
        request,
        application,
        form_data,
        action=ApplicationFormDataRecord.ACTION_TYPE_ASSIGN_VALUE):
    from wildlifecompliance.components.applications.utils import \
            MissingFieldsException
    can_edit_officer_comments = request.user.has_perm(
        'wildlifecompliance.licensing_officer'
    )
    can_edit_assessor_comments = request.user.has_perm(
        'wildlifecompliance.assessor'
    )
    can_edit_comments = can_edit_officer_comments \
        or can_edit_assessor_comments
    can_edit_deficiencies = request.user.has_perm(
        'wildlifecompliance.licensing_officer'
    )

    if action == ApplicationFormDataRecord.ACTION_TYPE_ASSIGN_COMMENT and\
            not can_edit_comments and not can_edit_deficiencies:
        raise Exception(
            'You are not authorised to perform this action!')

    is_draft = form_data.pop('__draft', False)
    visible_data_tree = application.get_visible_form_data_tree(
        form_data.items())
    required_fields = application.required_fields
    missing_fields = []

    for field_name, field_data in form_data.items():
        schema_name = field_data.get('schema_name', '')
        instance_name = field_data.get('instance_name', '')
        component_type = field_data.get('component_type', '')
        value = field_data.get('value', '')
        officer_comment = field_data.get('officer_comment', '')
        assessor_comment = field_data.get('assessor_comment', '')
        deficiency = field_data.get('deficiency_value', '')
        activity_id = field_data.get('licence_activity_id', '')
        purpose_id = field_data.get('licence_purpose_id', '')
        component_attribute = field_data.get('component_attribute', '')

        if ApplicationFormDataRecord.INSTANCE_ID_SEPARATOR in field_name:
            [parsed_schema_name, parsed_instance_name] = field_name.split(
                ApplicationFormDataRecord.INSTANCE_ID_SEPARATOR
            )
            schema_name = schema_name if schema_name \
                else parsed_schema_name
            instance_name = instance_name if instance_name \
                else parsed_instance_name

        try:
            visible_data_tree[instance_name][schema_name]
        except KeyError:
            continue

        form_data_record = ApplicationFormDataRecord.objects.filter(
            application_id=application.id,
            field_name=field_name,
            licence_activity_id=activity_id,
            licence_purpose_id=purpose_id,
        ).first()

        SPECIES = ApplicationFormDataRecord.COMPONENT_TYPE_SELECT_SPECIES
        if not form_data_record:
            form_data_record = ApplicationFormDataRecord.objects.create(
                application_id=application.id,
                field_name=field_name,
                schema_name=schema_name,
                instance_name=instance_name,
                component_type=component_type,
                licence_activity_id=activity_id,
                licence_purpose_id=purpose_id,
                component_attribute=component_attribute,
            )
        # Species list may not exist in last save because the component has
        # been copied from an amendment. Save new list for species component.
        elif form_data_record.component_type == SPECIES\
                and not form_data_record.component_attribute:
            form_data_record.component_attribute = component_attribute

        if action == ApplicationFormDataRecord.ACTION_TYPE_ASSIGN_VALUE:
            if not is_draft and not value \
                    and schema_name in required_fields:
                missing_item = {'field_name': field_name}
                missing_item.update(required_fields[schema_name])
                missing_fields.append(missing_item)
                continue
            form_data_record.value = value
        elif action == \
                ApplicationFormDataRecord.ACTION_TYPE_ASSIGN_COMMENT:
            if can_edit_officer_comments:
                form_data_record.officer_comment = officer_comment
            if can_edit_assessor_comments:
                form_data_record.assessor_comment = assessor_comment
            if can_edit_deficiencies:
                form_data_record.deficiency = deficiency
        form_data_record.save()

    if action == ApplicationFormDataRecord.ACTION_TYPE_ASSIGN_VALUE:
        do_update_dynamic_attributes(application)
        for existing_field in ApplicationFormDataRecord.objects.filter(
                application_id=application.id):
            if existing_field.field_name not in form_data.keys():
                existing_field.delete()

    if missing_fields:
        raise MissingFieldsException(
            [{'name': item['field_name'], 'label': '{label}'.format(
                label=item['label']
            )} for item in missing_fields]
        )


def do_update_dynamic_attributes(application):
    """ Update application and activity attributes based on selected JSON
        schema options.
    """
    if application.processing_status not in [
            Application.PROCESSING_STATUS_DRAFT,
            Application.PROCESSING_STATUS_AWAITING_APPLICANT_RESPONSE,
            Application.PROCESSING_STATUS_UNDER_REVIEW,
    ]:
        return

    # Get all fee adjustments made with check boxes and radio buttons.
    checkbox = CheckboxAndRadioButtonVisitor(application, application.data)
    for_increase_fee_fields = IncreaseApplicationFeeFieldElement()
    for_increase_fee_fields.set_updating(True)
    for_increase_fee_fields.accept(checkbox)
    dynamic_attributes = for_increase_fee_fields.get_dynamic_attributes()

    # Update application and licence fees
    fees = dynamic_attributes['fees']
    application.application_fee = fees['application']
    application.save()

    # Save any parsed per-activity modifiers
    for selected_activity, field_data in \
            dynamic_attributes['activity_attributes'].items():

        fees = field_data.pop('fees', {})
        selected_activity.licence_fee = fees['licence']
        selected_activity.application_fee = fees['application']

        # Check when under review for changes in fee amount.
        # Application fees can also be adjusted by internal officer.
        UNDER_REVIEW = Application.PROCESSING_STATUS_UNDER_REVIEW
        if application.processing_status == UNDER_REVIEW\
            and fees['application']\
                > selected_activity.base_fees['application']:
            selected_activity.application_fee = fees['application'] \
                - selected_activity.base_fees['application']

        # Check for refunds to Application Amendment, Renewals and Requested
        # Amendment Fees.
        REQUEST_AMEND = Application.CUSTOMER_STATUS_AMENDMENT_REQUIRED
        if application.application_type in [
            Application.APPLICATION_TYPE_AMENDMENT,
            Application.APPLICATION_TYPE_RENEWAL,
        ] or application.customer_status == REQUEST_AMEND:

            # set fee to zero when refund exists.
            if fees['application']\
                    < selected_activity.base_fees['application']:
                selected_activity.application_fee = Decimal(0.0)

        # Adjust fees to include the Increase Fee updated form questions.
        for_increase_fee_fields.set_adjusted_fees_for(selected_activity)

        for field, value in field_data.items():
            setattr(selected_activity, field, value)

        selected_activity.save()


"""
NOTE: Section for objects relating to the calculation of Application Fees.
"""


class ApplicationFeePolicy(object):
    """
    A Payment Policy Interface for Licence Applications.
    """
    __metaclass__ = abc.ABCMeta

    @staticmethod
    def get_fee_policy_for(application):

        AMEND = Application.APPLICATION_TYPE_AMENDMENT
        RENEW = Application.APPLICATION_TYPE_RENEWAL
        NEW = Application.APPLICATION_TYPE_NEW_LICENCE
        # New Activity is set for multiple activities on application.
        NEW_ACTIVITY = Application.APPLICATION_TYPE_ACTIVITY

        get_policy = {
            AMEND: ApplicationFeePolicyForAmendment(application),
            RENEW: ApplicationFeePolicyForRenew(application),
            NEW: ApplicationFeePolicyForNew(application),
            NEW_ACTIVITY: ApplicationFeePolicyForNew(application),
        }
        policy = get_policy.get(
            application.application_type,
            ApplicationFeePolicyForNew(application)
        )

        return policy

    @staticmethod
    def get_fee_product_lines_for(application):
        """
        Gets the checkout product lines for this application which inlcudes
        fee for both the application and licence activities.
        """
        product_lines = []

        # application.
        activities_with_fees = [
            a for a in application.activities if a.application_fee > 0]

        for activity in activities_with_fees:
            product_lines.append({
                'ledger_description': '{} (Application Fee)'.format(
                    activity.licence_activity.name),
                'quantity': 1,
                'price_incl_tax': str(activity.application_fee),
                'price_excl_tax': str(calculate_excl_gst(
                    activity.application_fee)),
                'oracle_code': ''
            })

        # licence activities.
        activities_with_fees = [
            a for a in application.activities if a.licence_fee > 0]

        for activity in activities_with_fees:
            product_lines.append({
                'ledger_description': '{} (Licence Fee)'.format(
                    activity.licence_activity.name),
                'quantity': 1,
                'price_incl_tax': str(activity.licence_fee),
                'price_excl_tax': str(calculate_excl_gst(
                        activity.licence_fee)),
                'oracle_code': ''
            })

        return product_lines

    @abc.abstractmethod
    def get_dynamic_attributes(self):
        """
        Gets dynamic attributes with adjustments to fees made by applying this
        policy.
        """
        pass

    @abc.abstractmethod
    def set_dynamic_attributes(self):
        """
        Sets dynamic attributes with any adjustments to fees applying this
        policy.
        """
        pass

    @abc.abstractmethod
    def set_dynamic_attributes_for(self, activity):
        '''
        Sets dynamic attributes for a Licence Activity/Purpose with any
        adjustments to fees applying this policy.
        '''
        pass

    @abc.abstractmethod
    def set_application_fee(self):
        """
        Sets the application fee from what was previously saved on the model.
        """
        pass


class ApplicationFeePolicyForAmendment(ApplicationFeePolicy):
    '''
    A fee policy that applies to an application for a licence amendment.
    - maintains a base application fee from previous application.
    - applies no licence fee.
    - all adjustment fees from the previous application are excluded.
    - adjustment fees based on questions are added to the application fee.
    '''
    AMEND = Application.APPLICATION_TYPE_AMENDMENT

    application = None
    dynamic_attributes = None   # Container for Activity fees.
    is_refreshing = False       # Flag indicating a page refresh.

    def __init__(self, application):
        self.application = application
        if self.application.application_type == self.AMEND:
            self.init_dynamic_attributes()

    def __str__(self):
        return 'Amend fee policy for {0}{1}'.format(
           'Application: {app} '.format(app=self.application.id),
           'attributes : {att} '.format(att=self.dynamic_attributes),
        )

    @staticmethod
    def set_zero_licence_fee_for(purpose):
        '''
        No base licence fees are paid for Amended Activity Purposes.
        '''
        if isinstance(purpose, ApplicationSelectedActivityPurpose):
            purpose.base_licence_fee = 0

    @staticmethod
    def set_previous_application_fee_for(purpose):
        '''
        The application fee is the same as the previous fee for Purpose.
        '''
        if isinstance(purpose, ApplicationSelectedActivityPurpose):
            previous = purpose.get_purpose_from_previous()
            prev_fee = previous.application_fee if previous else 0
            purpose.application_fee = prev_fee

    def init_dynamic_attributes(self):
        '''
        Initialise the dynamic attributes.
        '''
        self.is_refreshing = False
        application_fees = Application.calculate_base_fees(
                self.application.licence_purposes.values_list('id', flat=True)
            )['application']

        if self.application.application_fee > 0:
            # Apply previous application fee amount instead of base.
            prev_fees = self.application.previous_application.application_fee
            prev_fees = 0
            for activity in self.application.activities:
                prev = activity.get_activity_from_previous()
                purposes = prev.proposed_purposes.all() if prev else None
                for purpose in purposes:
                    prev_fees += purpose.application_fee

            application_fees = prev_fees

        self.dynamic_attributes = {
            'fees': {
                'application': application_fees,
                'licence': self.set_licence_fee(),
            },
            'activity_attributes': {},
        }

    def set_purpose_fees_for(self, activity):
        """
        Set all fees for the selected activity/purpose.
        """
        # get purposes from the application form.
        purpose_ids = ApplicationFormDataRecord.objects.filter(
            application_id=activity.application_id,
            licence_activity_id=activity.licence_activity_id,
        ).values_list('licence_purpose_id', flat=True).distinct()
        # set the selected activity purpose base fees.
        for p_id in purpose_ids:
            purpose = [p for p in activity.purposes if p.id == p_id]
            p, c = ApplicationSelectedActivityPurpose.objects.get_or_create(
                selected_activity_id=activity.id,
                purpose_id=purpose[0].id
            )
            previous = p.get_purpose_from_previous()
            prev_fee = previous.application_fee if previous else 0
            p.application_fee = prev_fee
            p.licence_fee = self.set_licence_fee()
            p.additional_fee = 0
            p.save()

    def set_licence_fee_to_zero_for(self, activity):
        """
        No licence fee is paid for amended Activity/Purpose
        """
        activity.licence_fee = 0

    def set_application_fee_to_previous_base_for(self, activity):
        """
        Application base fee is the same as previous application fee.

        NOTE: Same as amend_adjusted_fee(self, attributes)

        """
        self.set_purpose_fees_for(activity)
        prev_total = self.get_previous_paid_total_for(activity)
        prev_act = self.get_previous_paid_actual_for(activity)

        fees_adj = activity.application_fee         # Adjusted Fees.
        prev_adj = prev_total - prev_act            # Previous Adjustments.
        fees = prev_act + prev_adj                  # Total Fees.
        new_adj = fees_adj - fees                   # New Adjusments.
        activity.application_fee = prev_act
        if new_adj < 0:
            # No over-payments are reimbursed for Amendment applications - just
            # pay new calculated fee.
            activity.application_fee = fees_adj
        else:
            activity.application_fee += new_adj

    def get_previous_paid_total_for(self, activity):
        """
        Set Licence fee as an aggregated amount of all new Activity/Purposes
        which have been added as part of this Licence Amendment.
        """
        prev_total = 0
        for purpose in activity.proposed_purposes.all():
            prev = purpose.get_purpose_from_previous()
            prev_app_fee = prev.application_fee if prev else 0
            prev_adj_fee = prev.adjusted_fee if prev else 0
            prev_total += prev_app_fee
            prev_total += prev_adj_fee    # Fee from questions.

        prev_activity = activity.get_activity_from_previous()
        if prev_activity and prev_activity.has_adjusted_application_fee:
            prev_total += prev_activity.additional_fee

        return prev_total

    def get_previous_paid_actual_for(self, activity):
        """
        Set Licence fee as an aggregated amount of all new Activity/Purposes
        which have been added as part of this Licence Amendment.
        """
        prev_actual = 0
        for purpose in activity.proposed_purposes.all():
            prev_purpose = purpose.get_purpose_from_previous()
            prev_fee = prev_purpose.application_fee if prev_purpose else 0
            prev_actual += prev_fee

        return prev_actual

    def set_licence_fee(self):
        """
        Set Licence fee as an aggregated amount of all new Activity/Purposes
        which have been added as part of this Licence Amendment.
        """
        fee = 0

        return Decimal(fee)

    def set_application_fee(self):
        """
        Set Application fee from the saved model. Required when presentation is
        refreshed and no attributes are passed.
        """
        self.init_dynamic_attributes()
        self.is_refreshing = True

    def set_dynamic_attributes(self, attributes):
        '''
        Apply Licence Amendment Fee policy to dynamic attributes.
        '''
        if self.is_refreshing:
            return
        attributes = self.amend_adjusted_fee(attributes)

        self.dynamic_attrubutes = attributes

    def set_dynamic_attributes_for(self, activity):
        '''
        Apply Licence Amendment Fee policy to Activity fees.
        '''
        if self.is_refreshing:
            return
        self.set_licence_fee_to_zero_for(activity)
        self.set_application_fee_to_previous_base_for(activity)

    def amend_adjusted_fee(self, attributes):
        '''
        Amend only Application Fees for dynamic attributes.

        NOTE: Same as set_application_fee_to_previous_base_for(self, activity)

        '''
        prev_total = 0
        prev_act = 0
        new_act = 0
        fees_adj = 0

        for activity in self.application.activities:
            prev_total += self.get_previous_paid_total_for(activity)
            prev_act += self.get_previous_paid_actual_for(activity)
            # aggregate adjusted fees from calculated dynamic attributes.
            fees_adj += attributes[
                'activity_attributes'][activity]['fees']['application']

        prev_adj = prev_total - prev_act        # previous adjustments
        fees = prev_act + prev_adj + new_act    # total fees
        new_adj = fees_adj - fees               # new adjustments
        attributes['fees']['application'] = prev_act + new_act
        if new_adj < 0:
            # No over-payments are reimbursed for Amendment applications - just
            # pay new calculated fee.
            attributes['fees']['application'] = fees_adj
        else:
            attributes['fees']['application'] += new_adj

        return attributes

    def get_dynamic_attributes(self):
        return self.dynamic_attributes


class ApplicationFeePolicyForRenew(ApplicationFeePolicy):
    '''
    A fee policy that applies to an application to renew a licence.
    - maintains the application fee and licence fee from previous licence.
    - adjustment fees from the previous application are excluded.
    - adjustment fees based on questions are added to the application fee.
    '''
    RENEW = Application.APPLICATION_TYPE_RENEWAL

    is_refreshing = False       # Flag indicating a page refresh.

    def __init__(self, application):
        self._application = application
        if self._application.application_type == self.RENEW:
            self.init_dynamic_attributes()

    def __str__(self):
        return 'Renew fee policy for {0}{1}'.format(
           'Application: {app} '.format(app=self.application.id),
           'attributes : {att} '.format(att=self.dynamic_attributes),
        )

    def init_dynamic_attributes(self):
        self.is_refreshing = False
        self._dynamic_attributes = {
            'fees': Application.calculate_base_fees(
                self._application.licence_purposes.values_list('id', flat=True)
            ),
            'activity_attributes': {},
        }

    def set_application_fee(self):
        """
        Set Application fee from the saved model.
        """
        self.is_refreshing = True
        application_fees = Application.calculate_base_fees(
                self._application.licence_purposes.values_list('id', flat=True)
            )['application']
        licence_fees = Application.calculate_base_fees(
                self._application.licence_purposes.values_list('id', flat=True)
            )['licence']

        if self._application.application_fee > 0:
            application_fees = self._application.application_fee

        self._dynamic_attributes = {
            'fees': {
                'application': application_fees,
                'licence': licence_fees,
                },
            'activity_attributes': {},
        }

    def set_dynamic_attributes(self, attributes):
        if self.is_refreshing:
            return
        self._dynamic_attributes = attributes

    def get_dynamic_attributes(self):
        return self._dynamic_attributes

    def set_dynamic_attributes_for(self, activity):
        if self.is_refreshing:
            return


class ApplicationFeePolicyForNew(ApplicationFeePolicy):
    '''
    A fee policy that applies to an application for a new licence.
    - applies base purpose fees for both application and licence.
    - adjustment fees based on questions is added to the application fee.
    '''
    NEW = [
        Application.APPLICATION_TYPE_ACTIVITY,
        Application.APPLICATION_TYPE_NEW_LICENCE
    ]

    application = None
    dynamic_attributes = None   # Container for Activity fees.
    is_refreshing = False       # Flag indicating a page refresh.

    def __init__(self, application):
        self.application = application
        if self.application.application_type in self.NEW:
            self.init_dynamic_attributes()

    def __str__(self):
        return 'New fee policy for {0}{1}'.format(
           'Application: {app} '.format(app=self.application.id),
           'attributes : {att} '.format(att=self.dynamic_attributes),
        )

    def init_dynamic_attributes(self):
        self.is_refreshing = False
        self.dynamic_attributes = {
            'fees': Application.calculate_base_fees(
                self.application.licence_purposes.values_list('id', flat=True)
            ),
            'activity_attributes': {},
        }

    def set_purpose_fees_for(self, activity):
        """
        Set all fees for the selected activity/purpose.

        """
        # get purposes from the application form.
        purpose_ids = ApplicationFormDataRecord.objects.filter(
            application_id=activity.application_id,
            licence_activity_id=activity.licence_activity_id,
        ).values_list('licence_purpose_id', flat=True).distinct()
        # set the selected activity purpose base fees.
        for p_id in purpose_ids:
            purpose = [p for p in activity.purposes if p.id == p_id]
            p, c = ApplicationSelectedActivityPurpose.objects.get_or_create(
                selected_activity_id=activity.id,
                purpose_id=purpose[0].id
            )
            p.application_fee = purpose[0].base_application_fee
            p.licence_fee = purpose[0].base_licence_fee
            p.save()

    def set_application_fee(self):
        """
        Set Application fee from the saved model.
        """
        self.is_refreshing = True
        application_fees = Application.calculate_base_fees(
                self.application.licence_purposes.values_list('id', flat=True)
            )['application']
        licence_fees = Application.calculate_base_fees(
                self.application.licence_purposes.values_list('id', flat=True)
            )['licence']

        if self.application.application_fee > 0:
            application_fees = self.application.application_fee

        self.dynamic_attributes = {
            'fees': {
                'application': application_fees,
                'licence': licence_fees,
                },
            'activity_attributes': {},
        }

    def set_dynamic_attributes(self, attributes):
        if self.is_refreshing:
            return
        self.dynamic_attributes = attributes

    def get_dynamic_attributes(self):
        return self.dynamic_attributes

    def set_dynamic_attributes_for(self, activity):
        '''
        Sets any updated attribute fees associated with the Activity.
        '''
        if self.is_refreshing:
            return
        self.set_purpose_fees_for(activity)


"""
NOTE: Section for objects relating to generating Application species list.
"""


class TSCSpecieService():
    """
    Interface for Threatened Species Communities api services.
    """
    def __init__(self, call_strategy):
        self._strategy = call_strategy

    def set_strategy(self, call_strategy):
        self._strategy = call_strategy

    def get_strategy(self):
        return self._strategy

    def search_taxon(self, specie_id):
        """
        Search taxonomy for specie details and save search data.
        """
        try:
            token = None
            identifier = None
            search_data = self._strategy.request_species(specie_id)

            if search_data:
                if isinstance(self._strategy, TSCSpecieXReferenceCall):
                    token = search_data[0]['xref_id']
                    identifier = self._strategy._CODE

                # Save searched details.
                specie, verified = LicenceSpecies.objects.get_or_create(
                    specie_id=int(specie_id)
                )
                specie.verify_id = identifier
                specie.verify_token = token
                specie.data = search_data
                specie.save()  # save specie to update verification date.

            return search_data

        except BaseException:
            print "{} error: {}".format(self._strategy, sys.exc_info()[0])
            raise

    def __str__(self):
        return 'TSCSpecieService: {}'.format(self._strategy)


class TSCSpecieCallStrategy(object):
    """
    A Strategy Interface declaring a common operation for the TSCSpecie Call.
    """

    _AUTHORISE = {"Authorization": settings.TSC_AUTH}
    _CODE = None

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def request_species(self, species):
        """
        Operation for consuming TSCSpecie details.
        """
        pass


class TSCSpecieCall(TSCSpecieCallStrategy):
    """
    A TSCSpecie Call.
    """
    _CODE = 'TAXON'
    _URL = "https://tsc.dbca.wa.gov.au/api/1/taxon/?format=json"

    def __init__(self):
        super(TSCSpecieCallStrategy, self).__init__()
        self._depth = sys.getrecursionlimit()

    def set_depth(self, depth):
        """
        Set the number of recursion levels.
        """
        self._depth = depth if depth > 0 else sys.getrecursionlimit()

    def request_species(self, specie_id):

        def send_request(specie_id):
            url = '{0}&name_id={1}'.format(self._URL, specie_id)
            specie_json = requests.get(url, headers=self._AUTHORISE).json()
            return specie_json

        details = send_request(specie_id)
        specie = {
            'name_id': details['features'][0]['name_id'],
            'name':  details['features'][0]['name'],
            'canonical_name': details['features'][0]['canonical_name'],
            'vernacular_name': details['features'][0]['vernacular_name'],
            }

        return specie


class TSCSpecieRecursiveCall(TSCSpecieCallStrategy):
    """
    A Recursive strategy for the TSCSpecie Call.
    To be implemented. Recursive action on TSC server-side.
    """
    _CODE = 'TAXON1'

    def __init__(self):
        super(TSCSpecieCallStrategy, self).__init__()
        self._depth = sys.getrecursionlimit()

    def set_depth(self, depth):
        pass

    def request_species(self, species):
        pass

    def __str__(self):
        return 'Recursive call with max depth {}'.format(self.depth)


class TSCSpecieXReferenceCall(TSCSpecieCallStrategy):
    """
    A Recursive strategy for the TSCSpecie Call.

    Reason 0: Misapplied name
    Reason 1: Taxonomic synonym
    Reason 2: Nomenclatural synonym
    Reason 3: Excluded name
    Reason 4: Concept change
    Reason 5: Formal description
    Reason 6: Orthographic variant
    Reason 7: Name in error
    Reason 8: Informal Synonym
    """
    _CODE = "XREF"
    _XREF = "https://tsc.dbca.wa.gov.au/api/1/crossreference/?format=json"
    _TAXN = "https://tsc.dbca.wa.gov.au/api/1/taxon-fast/?format=json"

    def __init__(self):
        super(TSCSpecieCallStrategy, self).__init__()
        self._depth = sys.getrecursionlimit()

    def set_depth(self, depth):
        """
        Set the number of recursion levels.
        """
        self._depth = depth if depth > 0 else sys.getrecursionlimit()

    def request_species(self, species):
        LEVEL = 0
        level_list = [{'name_id': species}]

        return self.get_level_species(LEVEL, level_list)

    def get_level_species(self, level_no, level_species):
        requested_species = []

        def send_request_successor(level_species):
            # sends a request to TSC for each specie in level using specie_id
            # to retrieve successors.
            level_list = []
            for specie in level_species:

                # check if verified and recursively decend from that token.
                try:
                    xref_id = LicenceSpecies.objects.values(
                        'verify_token').get(specie_id=specie['name_id'])

                    return send_request_token(xref_id['verify_token'])

                except LicenceSpecies.DoesNotExist:
                    pass
                except KeyError:
                    pass

                url = '{0}&predecessor__name_id={1}'.format(
                    self._XREF, specie['name_id'])
                xref = requests.get(url, headers=self._AUTHORISE).json()

                if (xref['count'] and xref['count'] > 0):
                    xref['results'][0]['successor'][
                        'authorised_on'] = xref['results'][0]['authorised_on']
                    xref['results'][0]['successor'][
                        'xref_id'] = xref['results'][0]['xref_id']
                    level_list.append(xref['results'][0]['successor'])

            return level_list

        def send_request_node(level_species):
            # Sends a request to TSC for each specie in level using specie id
            # to retrieve specie details.
            level_list = []
            for specie in level_species:

                url = '{0}&name_id={1}'.format(
                    self._TAXN, specie['name_id'])
                taxon = requests.get(url, headers=self._AUTHORISE).json()

                if (taxon['count'] and taxon['count'] > 0):
                    taxon['features'][0]['authorised_on'] = None
                    taxon['features'][0]['xref_id'] = 0
                    level_list.append(taxon['features'][0])

            return level_list

        def send_request_token(xref_id):
            # Send a request to TSC using xref identifier to retrieve
            # successors.
            level_list = []
            for specie in level_species:

                url = '{0}&xref_id={1}'.format(
                    self._XREF, xref_id)
                xref = requests.get(url, headers=self._AUTHORISE).json()

                if (xref['count'] and xref['count'] > 0):
                    xref['results'][0]['successor'][
                        'authorised_on'] = xref['results'][0]['authorised_on']
                    xref['results'][0]['successor'][
                        'xref_id'] = xref['results'][0]['xref_id']
                    level_list.append(xref['results'][0]['successor'])

            return level_list

        # recursive descent.
        level_no = level_no + 1
        if level_no < self._depth:  # stopping rule.
            successor = send_request_successor(level_species)
            requested_species = successor
            if successor:
                next_level_species = self.get_level_species(
                    level_no, successor)

                for specie in next_level_species:
                    requested_species.append(specie)
        else:
            raise Exception('{0} - Recursion limit exceeded.'.format(self))

        if not requested_species and level_no < 2:
            # When no successor from root retrieve root node.
            requested_species = send_request_node(level_species)

        return requested_species

    def __str__(self):
        return 'XRef call with max depth {}'.format(self._depth)
