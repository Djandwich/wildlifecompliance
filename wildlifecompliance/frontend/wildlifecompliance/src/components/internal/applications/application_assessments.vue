<template lang="html">
    <div class="row">
        <template v-if="isApplicationLoaded && initialiseAssessmentOptions()">

            <modal
                transition="modal fade"
                :showOk="false"
                @cancel="close()"
                title="Assessment Record" large>
                <div class="container-fluid">
                    <div class="row">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3 class="panel-title">Assessment Details
                                    <a class="panelClicker" :href="'#'+panelBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="panelBody">
                                        <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                    </a>
                                </h3>
                            </div>
                            <div class="panel-body panel-collapse collapse in" :id="panelBody">
                                <form class="form-horizontal" name="assessment_form" method="put">
                                    <div class="col-sm-12">
                                        <div class="form-group">
                                            <div class="row">
                                                <div class="col-sm-3">
                                                    <label class="control-label pull-left">Final Comments</label>
                                                </div>
                                                <div class="col-sm-9">
                                                    <textarea class="form-control" v-model="assessment.final_comment" :readonly="!canCompleteAssessment" style="width: 100%; max-width: 100%;" />
                                                </div>
                                            </div>
                                        </div>
                                        <div class="row" v-if="canCompleteAssessment">
                                            <div class="col-sm-12">
                                                <button v-if="!savingAssessment" @click.prevent="saveAssessment()" class="btn btn-primary pull-right assessment-button">Save Assessment</button>
                                                <button v-if="!savingAssessment" @click.prevent="completeAssessment()" class="btn btn-primary pull-right assessment-button">Mark Complete</button>
                                                <button v-else disabled class="btn btn-primary pull-right"><i class="fa fa-spin fa-spinner"></i>&nbsp;Saving</button>
                                            </div>
                                        </div>
                                    </div>
                                    
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </modal>

            <div>
                <ul id="tabs-assessor" class="nav nav-pills mb-3">
                    <li class="nav-item" v-for="(item1,index) in applicationActivities" :class="setAssessorTab(index)" @click.prevent="clearSendToAssessorForm()">
                        <a class="nav-link" v-if="isActivityVisible(item1.id)" data-toggle="pill" :data-target="`#${item1.id}`">{{item1.name}}</a>
                    </li>
                </ul>
            </div>
                
            <div class="tab-content">
                <div v-if="selectedActivity" :id="`${selectedActivity.id}`">
                    <div>
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3 class="panel-title">{{canSendToAssessor ? 'Send to Assessor' : 'Assessments'}}
                                    <a class="panelClicker" :href="`#${selectedActivity.id}`+assessorsBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="assessorsBody">
                                        <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                    </a>
                                </h3>
                            </div>
                            <div class="panel-body panel-collapse collapse in" :id="`${selectedActivity.id}`+assessorsBody">
                                <div v-if="canSendToAssessor" class="row">
                                    <div class="col-sm-10" style="margin-bottom: 10px">
                                            <label class="control-label pull-left"  for="Name">Assessor Group</label>
                                            <select class="form-control" v-model="selectedAssessor">
                                                <option 
                                                    v-for="(assessor, idx) in assessorGroup"
                                                    v-if="isAssessorRelevant(assessor)"
                                                    :id="assessor.id"
                                                    :value="assessor"
                                                    :selected="!selectedAssessor"
                                                >{{assessor.display_name}}</option>
                                            </select>
                                    </div>
                                    <div class="col-sm-2">
                                        <a class="btn btn-primary" v-show="showSendToAssessorButton" style="cursor:pointer;text-decoration:none;" @click.prevent="sendtoAssessor(selectedActivity.id)">Send</a>
                                    </div>
                                </div>
                                <div class="row" v-if="optionsLoadedForActivity(selectedActivity)" v-bind:key="`assessor_datatable_${selectedActivity.id}`">
                                    <datatable ref="assessorDatatable"
                                        :data-index="selectedActivity.id"
                                        :id="`${selectedActivity.id}_${_uid}assessor_datatable`"
                                        :dtOptions="assessors_options[selectedActivity.id]"
                                        :dtHeaders="assessors_headers"
                                        :onMount="eventListeners"/>
                                </div>
                            </div>
                        </div>
                        <div :id="`${selectedActivity.id}`" class="tab-pane fade in">
                            <Conditions
                                :key="`assessor_condition_${selected_activity_tab_id}`"
                                :final_view_conditions="final_view_conditions"
                                :activity="selectedActivity"/>
                        </div>
                    </div>
                </div>
            </div>
        </template>
        <SendToAssessor ref="send_to_assessor" @refreshFromResponse="refreshFromResponse"></SendToAssessor>
    </div>
</template>
<script>
import Application from '../../form.vue';
import Vue from 'vue';
import modal from '@vue-utils/bootstrap-modal.vue'
import datatable from '@vue-utils/datatable.vue';
import { mapActions, mapGetters } from 'vuex'
import Conditions from './application_conditions.vue';
import SendToAssessor from './application_send_assessor.vue';
import ResponsiveDatatablesHelper from "@/utils/responsive_datatable_helper.js";
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks';
export default {
    name: 'ApplicationAssessments',
    data: function() {
        let vm = this.$parent;
        return {
            assessment: {
                id: "",
                comment: "",
            },
            datepickerInitialised: false,
            isModalOpen: false,
            assessorsBody: `assessorsBody${vm._uid}`,
            assessorGroup: [],
            panelBody: `assessment-details-${vm._uid}`,
            "selectedAssessor": {},
            application_assessor_datatable: `${vm._uid}assessment-table`,
            assessors_headers: ["Assessor Group","Date Sent","Status","Final Comments","Action"],
            assessors_options: {},
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            viewingAssessmentId: null,
            savingAssessment: false,
            showSendToAssessorButton: true,
        }
    },
    components: {
        datatable,
        modal,
        Application,
        Conditions,
        SendToAssessor,
    },
    props:{
        final_view_conditions: {
            type: Boolean,
            default: false,
        },
    },
    filters: {
        formatDate: function(data){
            return data ? moment(data).format('DD/MM/YYYY HH:mm:ss'): '';
        }
    },
    watch: {
    },
    computed: {
        ...mapGetters([
            'application',
            'original_application',
            'licence_type_data',
            'selected_activity_tab_id',
            'selected_activity_tab_name',
            'hasRole',
            'visibleConditionsFor',
            'licenceActivities',
            'checkActivityStatus',
            'isPartiallyFinalised',
            'isFinalised',
            'isApplicationLoaded',
            'isApplicationActivityVisible',
            'unfinishedActivities',
            'current_user',
            'sendToAssessorActivities',
            'canAssignOfficerFor',
            'allCurrentActivities',
            'allCurrentActivitiesWithAssessor',
        ]),
        isCompleteAssessmentAction: function() {
            return this.$router.currentRoute.name==='complete-assessment'
        },
        applicationActivities: function() {

            if (this.isCompleteAssessmentAction){

                // filtered activity list for application when completing assessments.
                return this.allCurrentActivitiesWithAssessor
            }
            return this.licenceActivities()
        },
        selectedActivity: function(){
            const activities_list = this.licence_type_data.activity;
            for(let activity of activities_list){
                if(activity.id == this.selected_activity_tab_id){
                    return activity;
                }
            }
            return null;
        },
        isLicensingOfficer: function() {
            return this.userHasRole('licensing_officer', this.selected_activity_tab_id);
        },
        canCompleteAssessment: function() {
            if(!this.userHasRole('assessor', this.selected_activity_tab_id)) {
                return false;
            }
            if(this.assessment.status && this.assessment.status.id != 'awaiting_assessment'){
                return false;
            }
            return this.selected_activity_tab_id && this.selectedActivity.processing_status.id == 'with_assessor' ? true : false;
        },
        canSendToAssessor: function() {
            this.showSendToAssessorButton = false;
            if (this.$router.currentRoute.name=='complete-assessment'){
                // complete assessment route is only for assessors.
                return null;
            }            
            if (!this.canAssignOfficerFor(this.selected_activity_tab_id)) {
                // officer has no permissions for licence activity.
                return null;
            }
            // check activity is not assigned to another officer.
            var selectedActivity = this.application.activities.find(activity => {
                return activity.licence_activity === this.selected_activity_tab_id;
            });
            if (selectedActivity.assigned_officer != null && selectedActivity.assigned_officer !== this.current_user.id) {
                return false;
            };
            
            return this.sendToAssessorActivities.filter(visible_activity => {
                if(visible_activity.id != this.selected_activity_tab_id) {
                    return false;
                }
                for(const assessor of this.assessorGroup) {
                   if(assessor.licence_activities && assessor.licence_activities.filter(
                           activity => {
                                if(activity.id === visible_activity.id) {

                                    return true; // this assessor is for activity.
                                }
                                return false;
                            }
                    ).length) { // can send to this assessor
                        if (!this.isAssessorAssigned(assessor, visible_activity.id)) {

                            if(this.selectedAssessor.id == null || !this.assessorInGroup(this.selectedAssessor.id)) {
                                // Pre-select default Assessor Group drop-down option for the current tab
                                this.selectedAssessor = assessor;
                            }
                            this.showSendToAssessorButton = true;
                            return true;
                        };
                    }
                }
                return false; // no assessors in group.
            }).length;
        },
    },
    methods: {
        ...mapActions({
            load: 'loadApplication',
            revert: 'revertApplication',
        }),
        ...mapActions([
            'setApplication',
            'setActivityTab',
        ]),
        close: function () {
            this.isModalOpen = false;
        },
        openAssessmentModal: function(assessment_id) {
            this.isModalOpen = true;
            this.viewingAssessmentId = assessment_id;
            this.$http.get(`${api_endpoints.assessment}${this.viewingAssessmentId}`).then((response) => {
                    this.assessment = response.body;
            },(error) => {
                console.log(error);
            })
        },
        saveAssessmentData: function(e) {
            return new Promise((resolve, reject) => {
                let formData = new FormData(this.form);
                formData.append('final_comment', this.assessment.final_comment);
                this.$http.put(helpers.add_endpoint_json(api_endpoints.assessment,this.assessment.id+'/update_assessment'),formData,{
                    emulateJSON:true
                }).then(res=>{
                    resolve(res);
                },err=>{
                    reject(err);
                });
            })
        },
        saveAssessment: function(e) {
            this.savingAssessment = true;
            this.saveAssessmentData().then(() => {
                swal(
                    'Save Assessment',
                    'Your assessment has been saved.',
                    'success'
                ).then((result) => {
                    this.savingAssessment = false;
                });
            }, error => {
                swal(
                    'Error',
                    'There was an error saving your assessment',
                    'error'
                ).then((result) => {
                    this.savingAssessment = false;
                })
            });
        },
        canEditAssessment: function(assessment) {
            // Check current user is assigned assessor.
            return assessment.assigned_assessor && assessment.assigned_assessor.id===this.current_user.id
        },  
        userHasRole: function(role, activity_id) {

            // check activity is not assigned to another officer.
            var selectedActivity = this.application.activities.find(activity => {
                return activity.licence_activity === this.selected_activity_tab_id;
            });
            if (selectedActivity.assigned_officer != null && selectedActivity.assigned_officer !== this.current_user.id) {
                return false;
            };

            return this.hasRole(role, activity_id);
        },
        getVisibleConditionsFor: function(for_role, processing_status, tab_id) {
            return this.visibleConditionsFor(for_role, processing_status, tab_id);
        },
        initFirstTab: function(force){
            if(this.selected_activity_tab_id && !force) {
                return;
            }
            let tab = null
            let first_tab = null 
            if (this.isCompleteAssessmentAction){
                // force first_tab if parent tabs not created. 
                first_tab = this.selected_activity_tab_id
                // Set tab for parent component in completing assessments.
                let tabs = $('#tabs-assessor li')
                for (let i=0; i < tabs.length; i++){

                    if (tabs[i].innerText===this.selected_activity_tab_name){
                        // set parent tab to selected tab.
                        tab = $('#tabs-assessor li a')[i]
                    }
                }
            } else {
                first_tab = this.applicationActivities[0].id
            }
            if(tab) {
                tab.click();
            }
            else { // force first tab selection attributes.

                this.licenceActivities().filter(activity => {
                    if (activity.id==first_tab) {

                        this.setActivityTab({ id: activity.id, name: activity.name });
                    }
                })
            }
        },
        assessorInGroup: function(assessor_id) {
            return this.assessorGroup.filter(assessor => assessor.id == assessor_id).length;
        },
        isActivityVisible: function(activity_id) {
            //return this.isApplicationActivityVisible({ activity_id: activity_id });
            return 1
        },
        isAssessorRelevant(assessor, activity_id) {
            if(!activity_id) {
                activity_id = this.selected_activity_tab_id;
            }
            if(!assessor.licence_activities) {
                return false;
            }
            var isForActivity = assessor.licence_activities.find(activity => {

                return activity.id === activity_id; 
            });

            return isForActivity && !this.isAssessorAssigned(assessor, activity_id)
        },
        isAssessorAssigned(assessor, activity_id) {
            return this.application.assessments.find(assessment => {
 
                return assessment.assessor_group.id === assessor.id
                    && assessment.licence_activity === activity_id;               
            });
        },
        sendtoAssessor: function(item1){
            let vm=this;
            this.$refs.send_to_assessor.assessment.licence_activity=item1;
            this.$refs.send_to_assessor.assessment.assessor_group=this.selectedAssessor.id;
            this.$refs.send_to_assessor.assessment.assessor_group_name=this.selectedAssessor.display_name;
            this.$refs.send_to_assessor.assessment.licence_activity=this.selected_activity_tab_id;
            this.$refs.send_to_assessor.assessment.text='';
            if (this.selectedAssessor.id == null || this.selectedAssessor.display_name == null){
              swal(
                'Error',
                'Please select an Assessor Group to send the request to.',
                'error'
              )
            } else {
                this.$refs.send_to_assessor.isModalOpen=true;
            }
        },
        clearSendToAssessorForm(){
            this.$refs.send_to_assessor.assessment.text='';
            this.selectedAssessor={};
        },
        hasActivityStatus: function(status_list, status_count=1, required_role=null) {
            return this.checkActivityStatus(status_list, status_count, required_role);
        },
        setAssessorTab(_index){
            return _index === 0 ? 'active' : '';
        },
        refreshAssessorDatatables: function(){
            this.$refs.assessorDatatable.vmDataTable.ajax.reload();
        },
        completeAssessment: function(){
            this.saveAssessmentData().then(() => {
                let data = new FormData();

                data.selected_assessment_tab=this.selected_activity_tab_id;
                data.application_id=this.application.id;
                
                this.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(this.application.id+'/complete_assessment')),
                {
                    "selected_assessment_tab": this.selected_activity_tab_id,
                    "application_id": this.application_id,
                    "assessment_id": this.viewingAssessmentId,
                })
                .then((response) => {
                    // FIXME: $parent causing local flags to loose settings
                    // and therefore not closing. Should be ok as assessor
                    // does not update applications.
                    // this.$parent.refreshFromResponse(response);
                    this.refreshAssessorDatatables();
                    this.close();
                    swal(
                        'Complete Assessment',
                        'The assessment has been successfully completed',
                        'success'
                    )
                }, (error) => {
                    this.revert();
                    swal(
                        'Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                });
            }, error => {
                swal(
                    'Error',
                    helpers.apiVueResourceError(error),
                    'error'
                );
            });
        },
        refreshFromResponse: function(response){
            this.$parent.refreshFromResponse(response);
            this.fetchAssessorGroup();
            this.refreshAssessorDatatables();
        },
        fetchAssessorGroup: function(){
            let data = {'application_id' : this.application.id };
            this.$http.post(helpers.add_endpoint_json(api_endpoints.assessor_group,'user_list'),JSON.stringify(data),{
                emulateJSON:true,
            }).then((response) => {
                this.assessorGroup = response.body;
            },(error) => {
                console.log(error);
            });
        },
        initialiseAssessmentOptions: function() {
            if(!this.isApplicationLoaded) {
                return false;
            }
            const vm = this;
            for (let activity of this.licence_type_data.activity) {
                //Check for permissions
                if(this.assessors_options[activity.id] != null) {
                    continue;
                }
                this.assessors_options[activity.id] = {
                     language: {
                        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                    },
                    responsive: true,
                    ajax: {
                        "url": helpers.add_endpoint_join(api_endpoints.applications,this.application.id+'/assessment_details/?licence_activity='+activity.id),
                        "dataSrc": ''
                    },
                    columns: [
                        {data:'assessor_group.display_name'},
                        {data:'date_last_reminded'},
                        {data:'status.name'},
                        {data:'final_comment'},
                        {
                            data: "id",
                            mRender:function (data,type,full) {
                                let links = '';
                                const pending = full.status.id === 'awaiting_assessment';
                                if(['completed','recalled'].includes(full.status.id) && vm.userHasRole('licensing_officer', vm.selected_activity_tab_id)){
                                    links +=  `
                                        <a data-assessmentid='${full.id}' class="assessment-action assessment_resend">Resend</a>
                                    `;
                                } else if(pending && vm.userHasRole('licensing_officer', vm.selected_activity_tab_id)){
                                    links +=  `
                                        <a data-assessmentid='${full.id}' class="assessment-action assessment_remind">Remind</a>
                                        <a data-assessmentid='${full.id}' class="assessment-action assessment_recall">Recall</a>
                                    `;
                                }
                                if (!vm.isCompleteAssessmentAction) {
                                    links +=  `
                                        <a data-assessmentid='${full.id}' class="assessment-action assessment_view">${pending && vm.canEditAssessment(full)? 'Edit' : 'View'}</a>
                                    `;
                                }

                                return links;
                            }}
                    ],
                    processing: true
                }
            }

            return true;
        },
        optionsLoadedForActivity(activity) {
            return this.assessors_options[activity.id] != null;
        },
        readFileInspectionReport: function() {
            let _file = null;
            var input = $(this.$refs.inspection_report)[0];
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(input.files[0]);
                reader.onload = function(e) {
                    _file = e.target.result;
                };
                _file = input.files[0];
            }
            this.assessment.inspection_report = _file;
        },
        eventListeners: function(){
            let vm = this;
            this.initFirstTab();
            // Listeners for Send to Assessor datatable actions
            if (!this.$refs.assessorDatatable) {
                return false;
            }

            this.$refs.assessorDatatable.vmDataTable.on('click','.assessment_remind',(e) => {
                e.stopImmediatePropagation();
                e.preventDefault();

                let assessment_id = $(e.target).data('assessmentid');
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.assessment,(assessment_id+'/remind_assessment'))).then((response)=>{
                    swal(
                            'Sent',
                            'An email has been sent to assessor with the request to assess this Application',
                            'success'
                    )
                    vm.refreshAssessorDatatables();
                },(error)=>{
                    console.log(error);
                    vm.errors = true;
                    vm.errorString = helpers.apiVueResourceError(error);


                });
            });

            this.$refs.assessorDatatable.vmDataTable.on('click','.assessment_resend',(e) => {
                e.stopImmediatePropagation();
                e.preventDefault();

                let assessment_id = $(e.target).data('assessmentid');
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.assessment,(assessment_id+'/resend_assessment'))).then((response)=>{
                    swal(
                            'Sent',
                            'An email has been sent to assessor with the request to re-assess this Application',
                            'success'
                    )
                    vm.refreshAssessorDatatables();
                    vm.$http.get(helpers.add_endpoint_json(api_endpoints.applications,vm.application.id+'/internal_application')).then((res) => {
                        vm.refreshFromResponse(res);
                    });

                },(error)=>{
                    console.log(error);
                    vm.errors = true;
                    vm.errorString = helpers.apiVueResourceError(error);


                });
            });

            this.$refs.assessorDatatable.vmDataTable.on('click','.assessment_recall',(e) => {
                e.stopImmediatePropagation();
                e.preventDefault();

                let assessment_id = $(e.target).data('assessmentid');
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.assessment,(assessment_id+'/recall_assessment'))).then((response)=>{
                    //vm.$parent.loading.splice('processing contact',1);
                    swal(
                            'Success',
                            'An assessment for this Application has been recalled',
                            'success'
                    )
                    vm.refreshAssessorDatatables();
                    vm.$http.get(helpers.add_endpoint_json(api_endpoints.applications,vm.application.id+'/internal_application')).then((res) => {
                        vm.refreshFromResponse(res);
                    });
                },(error)=>{
                    console.log(error);
                    vm.errors = true;
                    vm.errorString = helpers.apiVueResourceError(error);


                });
            });

            this.$refs.assessorDatatable.vmDataTable.on('click','.assessment_view',(e) => {
                const assessment_id = $(e.target).data('assessmentid');
                this.openAssessmentModal(assessment_id);
                e.preventDefault();
            });
        },
    },
    mounted: function() {
        this.fetchAssessorGroup();
        this.initFirstTab(true);
        this.$nextTick(() => {
            this.eventListeners();
        });
    },
}

</script>
<style scoped>

</style>
