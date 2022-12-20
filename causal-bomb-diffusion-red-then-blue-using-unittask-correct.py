import sys

# put Python ACT-R working dir here.
sys.path.append('C:/Users/nh_or/Documents/cogmodelling/CCMSuite3-master/CCMSuite3-master')

import ccm

log = ccm.log()

# log=ccm.log(html=True)

from ccm.lib.actr import *


# --------------- Environment ------------------

class MyEnvironment(ccm.Model):

    bomb = ccm.Model(state='armed')

    red_wire = ccm.Model(isa='wire', state='uncut', color='red', salience=0.99)
    blue_wire = ccm.Model(isa='wire', state='uncut', color='blue', salience=0.99)
    green_wire = ccm.Model(isa='wire', state='uncut', color='green', salience=0.99)


######## SET THE BOMB #########

## Change self.blue_wire and self.red_wire to alter disarmament protocol

    def wires(self, wire1, wire2):
        if wire1 == self.red_wire and wire1.state == 'cut':
            if wire2 == self.blue_wire and wire2.state == 'cut':
                self.bomb.state = 'disarmed'
                print("disarmed")
            else:
                count = 1
                print("still armed")
                pass
        else:
            print("still armed")
            pass

    motor_finst = ccm.Model(isa='motor_finst', state='re_set')

class MotorModule(ccm.Model):  ### defines actions on the environment

# change_state is a generic action that changes the state slot of any object
# disadvantages (1) yield time is always the same (2) cannot use for parallel actions

    def change_state(self, env_object, slot_value):
        yield 2
        x = eval('self.parent.parent.' + env_object)
        x.state = slot_value
        #print env_object
        #print slot_value
        self.parent.parent.motor_finst.state = 'finished'
        
    def motor_finst_reset(self):
        self.parent.parent.motor_finst.state = 're_set'
    
    # Note this is not ideal atm. This is a temporary replacement for episodic memory
    # and currently doesn't work ideally. Once episodic, it should remember the cutting, not just check whether they've been cut.
    def watchBomb(self, cue):
        self.parent.parent.wires(self.parent.parent.red_wire, self.parent.parent.blue_wire)
        if cue == 'X':
            if self.parent.parent.blue_wire.state == 'cut':
                if self.parent.parent.red_wire.state == 'cut':
                    if self.parent.parent.bomb.state == 'disarmed':
                        print("Cutting the blue then the red wire was correct.")
                        print("The bomb has been disarmed.")
                        self.parent.DM.add('object:bomb state:disarmed time:1')
                    else:
                        print("Cutting blue then red was incorrect.")
                        print("The bomb is still armed.")
                        self.parent.DM.add('object:bomb state:armed time:1')
                else:
                    print("I haven't cut the red wire yet.")
            else:
                print("No wires have been cut.")                            
        elif cue == 'Y':
            if self.parent.parent.red_wire.state == 'cut':
                if self.parent.parent.blue_wire.state == 'cut':
                    if self.parent.parent.bomb.state == 'disarmed':
                        print("Cutting the red then the blue wire was correct.")
                        print("The bomb has been disarmed.")
                        self.parent.DM.add('object:bomb state:disarmed time:1')
                    else:
                        print("Cutting the red then blue was incorrect.")
                        print("The bomb is still armed.")
                        self.parent.DM.add('object:bomb state:armed time:1')
                else:
                    print("I haven't cut the blue wire yet.")        
            else:
                print("No wires have been cut.")
        else:
            print("I have no plan for this.")



# --------------- Motor Method Module ------------------

class MethodModule(ccm.ProductionSystem):  # creates an extra production system for the motor system
    production_time = 0.04

# --------------- Vision Module ------------------

class VisionModule(ccm.ProductionSystem):
    production_time = 0.045


# --------------- Emotion Module ------------------

class EmotionalModule(ccm.ProductionSystem):
    production_time = 0.043


# --------------- Agent ------------------

class MyAgent(ACTR):
    ########### create agent architecture ################################################
    #############################################################

    # module buffers
    b_DM = Buffer()
    b_motor = Buffer()
    b_visual = Buffer()
    b_image = Buffer()
    b_focus = Buffer()
    b_episode = Buffer()

    # goal buffers
    b_context = Buffer()
    b_plan_unit = Buffer()  # create buffers to represent the goal module
    b_unit_task = Buffer()
    b_method = Buffer()
    b_operator = Buffer()
    b_emotion = Buffer()

    # associative memory
    DM = Memory(b_DM)  # create the DM memory module

    # perceptual motor module
    vision_module = SOSVision(b_visual, delay=0)  # create the vision module
    motor = MotorModule(b_motor)  # put motor production module into the agent

    # auxillary production modules
    Methods = MethodModule(b_method)  # put methods production module into the agent
    Eproduction = EmotionalModule(b_emotion)  # put the Emotion production module into the agent
    p_vision = VisionModule(b_visual)


    ###### MODEL GOALS:
        ## The bomb is armed. Disarm it.
        ## Potential Outcomes
            # Null Outcome: If you follow the wrong plan you will fail to disarm it.
            # Target Outcome: If you follow the correct plan, you will disarm it.


    ######### PURE CONCEPTS: GROUND LEVEL ############

    ## Kantian categories, or Kantian Declarative Memories (KDM), are the cognitive factulties that allow for reasoning.
    ## Only KDMs required for causal reasoning in this task are present. 

    # Quality ('state') KDM
    DM.add('KDM:is is:is not:isnot') # real yes, on, 1
    #DM.add('KDM:can') # potential yes, on, 1

    # Negation KDM
    DM.add('KDM:not is:not') # negates

    # Not Class
    DM.add('KDM:isnot is:isnot not:is')

    # Classification KDM
    DM.add('KDM:a is:a a:a') # qualities are collected to classify/identify
    # EXAMPLE: DM.add(a:cat is:furry is:whiskered is:cute)

    # Categorical KDM
    DM.add('KDM:isa is:isa') # objects used as qualities to categorize

    # Quantity KDM
    # EXAMPLE: DM.add('all') or most, half, some, none, etc.

    # Location KDM
    # EXAMPLE: DM.add('here') or there, left, right, up, down, under, over

    # Action KDM
    DM.add('KDM:do is:do not:donot')

    # Inaction KDM
    DM.add('KDM:donot is:donot not:do')

    # Temporal KDM
    DM.add('KDM:then is:then')

    # State Change KDM
    DM.add('KDM:isthen is:isthen')



    ######### ASSOCIATION: RUNG 1 ############

    # Object Knowledge
    DM.add('a:object isa:object') # takes class KDM and makes it object knowledge
 
    DM.add('object:bomb isa:object')
    DM.add('object:wire isa:object')
    DM.add('object:red_wire isa:wire color:red')
    DM.add('object:blue_wire isa:wire color:blue')

    # Property Knowledge
    DM.add('a:property isa:property') #takes class KDM and makes it property knowledge

    DM.add('property:color isa:property')
    DM.add('color:red isa:color')
    DM.add('color:blue isa:color')

    # Action Knowledge
    DM.add('do:action isa:action') # takes action KDM and makes it action knowledge
    DM.add('do:none isa:donot') # the lack of action isa 'donot' KDM

    DM.add('action:arm isa:action')
    DM.add('action:disarm isa:action')
    DM.add('action:expose isa:action')
    DM.add('action:cut isa:action')

    DM.add('expose:red_wire is:expose')
    DM.add('expose:blue_wire is:expose')
    DM.add('cut:red_wire is:cut')
    DM.add('cut:blue_wire is:cut')

    # Post-Hoc Action State Knowledge
    DM.add('a:state isa:isthen') # takes state change KDM and makes it state knowledge

    DM.add('state:armed isa:state')
    DM.add('state:disarmed isa:state')

    DM.add('state:exposed isa:state')
    DM.add('state:unexposed isa:state')

    DM.add('state:cut isa:state')
    DM.add('state:uncut isa:state')

    # Object State Knowledge
    DM.add('object:bomb state:armed time:0')
    DM.add('object:red_wire state:unexposed state:uncut time:0')
    DM.add('objectLblue_wire state:unexposed state:uncut time:0')



    ######### INTERVENTION & COUNTERFACTUALS: RUNG 2 ############

    ## Knowledge of state changes based on actions taken

    # Intervention Knowledge of Action
    DM.add('a:interv do:action then:state') # takes action/inaction knowledge and makes it an intervention
    DM.add('a:interv do:none then:none')

    DM.add('interv_a:arm is:disarmed action:arm isthen:armed')
    DM.add('interv_a:disarm is:armed action:disarm isthen:disarmed')
    DM.add('interv_a:expose is:unexposed action:expose isthen:exposed')
    DM.add('interv_a:cut is:uncut action:cut isthen:cut')

    # Intervention Knowledge of Action on Objects at Method Level
    DM.add('interv_m:expose_red_wire is:unexposed cut:red_wire isthen:exposed')
    DM.add('interv_m:expose_blue_wire is:unexposed cut:blue_wire isthen:exposed')
    DM.add('interv_m:cut_red_wire is:uncut cut:red_wire isthen:cut')
    DM.add('interv_m:cut_blue_wire is:uncut cut:blue_wire isthen:cut')

    # Unit Task Knowledge
    DM.add('interv_ut:red_wire_UT interv_m1:expose_red_wire interv_m2:cut_red_wire')
    DM.add('interv_ut:blue_wire_UT interv_m1:expose_blue_wire interv_m2:cut_blue_wire')

    # Planning Unit Knowledge
    DM.add('interv0:Y interv1:red_wire_UT interv2:blue_wire_UT')
    DM.add('interv0:X interv1:blue_wire_UT interv2:red_wire_UT')



    ######### META-INFERENCE: RUNG 3 ############
       
    #DM.add('metainf:disarm object:bomb interv:X isthen:disarmed')

    #DM.add('metainf:disarm object:bomb interv1:red_wire_UT isthen:disarmed') # red wire cut first
    
    DM.add('metainf:disarm object:bomb interv2:blue_wire_UT isthen:disarmed') # blue wire cut second


    ######### EPISODIC ############

        ##Empty##



    ############ add planning units to declarative memory and set context buffer ###############

    def init():
        DM.add('planning_unit:XY         cuelag:none          cue:start          unit_task:X')
        DM.add('planning_unit:XY         cuelag:none         cue:start              unit_task:Y')
        DM.add('planning_unit:XY         cuelag:start             cue:X              unit_task:finished')
        DM.add('planning_unit:XY         cuelag:start             cue:Y              unit_task:finished')
        b_context.set('finished:nothing status:unoccupied')

    ############ add causal inference ###############

    def infer_metainf(b_context='finished:nothing status:unoccupied'):
        DM.request('metainf:disarm object:bomb interv:?interv isthen:disarmed')
        b_context.set('finished:nothing status:inferring1')

    def infer_metainf_plan(b_context='finished:nothing status:inferring1', b_DM=None, DM='error:True'):
        print("I don't recall a plan")
        DM.request('metainf:disarm object:bomb interv1:?ut1 isthen:disarmed')
        b_context.set('finished:nothing status:inferring2')

    def infer_metainf_cut1(b_context='finished:nothing status:inferring2', b_DM=None, DM='error:True'):
        print("I don't recall what to cut first")
        DM.request('metainf:disarm object:bomb interv2:?ut2 isthen:disarmed')
        b_context.set('finished:nothing status:inferring3')

    def infer_metainf_cut2(b_context='finished:nothing status:inferring3', b_DM=None, DM='error:True'):
        print("I don't recall what to cut second")
        DM.request('interv0:?interv interv1:?ut1 interv2:?ut2')
        b_context.set('finished:inferring status:unoccupied')

    def infer_interv_plan(b_context='finished:nothing status:inferring1',
               b_DM='metainf:disarm object:bomb interv:?interv isthen:disarmed'):
        DM.request('interv0:?interv interv1:?ut1 interv2:?ut2')
        b_context.set('finished:inferring status:unoccupied')

    def infer_interv_cut1(b_context='finished:nothing status:inferring2',
               b_DM='metainf:disarm object:bomb interv1:?ut1 isthen:disarmed'):
        DM.request('interv0:?interv interv1:?ut1 interv2:?ut2')
        print("I recall", ut1,"goes first")
        b_context.set('finished:inferring status:unoccupied')

    def infer_interv_cut2(b_context='finished:nothing status:inferring3',
               b_DM='metainf:disarm object:bomb interv2:?ut2 isthen:disarmed'):
        DM.request('interv0:?interv interv1:?ut1 interv2:?ut2')
        print("I recall", ut2,"goes second")
        b_context.set('finished:inferring status:unoccupied')

    ########### add episodic memories ###########

        ##None yet##

    ########### create productions for choosing planning units ###########

    ## these productions are the highest level of SGOMS and fire off the context buffer
    ## they can take any ACT-R form (one production or more) but must eventually call a planning unit and update the context buffer

    def run_sequence(b_context='finished:inferring status:unoccupied', b_DM='interv0:?interv interv1:?ut1 interv2:?ut2'):# status:unoccupied triggers the selection of a planning unit
        b_plan_unit.set('planning_unit:XY cuelag:none cue:start unit_task:?interv state:begin_sequence')# state: can be begin_situated or begin_sequence
        b_context.set('finished:nothing status:occupied')# update context status to occupied
        ##print 'sequence planning unit is chosen'

    ########## unit task set up ###########

    ## these set up whether it will be an ordered or a situated planning unit (forced it to be ordered)

    def setup_ordered_planning_unit(b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:begin_sequence'):
        b_unit_task.set('unit_task:?unit_task state:start type:ordered')
        b_plan_unit.set('planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running')
        ##print 'begin orderdered planning unit = ', planning_unit

    ## these manage the sequence if it is an ordered planning unit

    def request_next_unit_task(b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running',
                               b_unit_task='unit_task:?unit_task state:finished type:ordered'):
        DM.request('planning_unit:?planning_unit cuelag:?cue cue:?unit_task unit_task:?')
        b_plan_unit.set('planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:retrieve')  # next unit task
        ##print 'finished unit task = ', unit_task

    def retrieve_next_unit_task(b_plan_unit='state:retrieve',
                                b_DM='planning_unit:?planning_unit cuelag:?cuelag cue:?cue!finished unit_task:?unit_task'):
        b_plan_unit.set('planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running')
        b_unit_task.set('unit_task:?unit_task state:start type:ordered')
        ##print 'unit_task = ', unit_task

    def last_unit_task_ordered(b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running',
                               b_unit_task='unit_task:finished state:start type:ordered'):
        ##print 'finished planning unit=',planning_unit
        ##print planning_unit
        b_unit_task.set('observe')
        b_context.set('finished:?planning_unit status:unoccupied')



    ################# unit tasks #################

    ## X unit task
    ## This unit task represents a routine situation where the bomb technician must expose and cut,
    ## first a blue wire then a red wire
        
    def X_unit_task_ordered(b_unit_task='unit_task:X state:start type:ordered'):
        b_unit_task.set('unit_task:X state:begin type:ordered')
        ##print 'start unit task X ordered'

    ## the first production in the unit task must begin in this way
    def X_start_unit_task(b_unit_task='unit_task:X state:begin type:?type'):
        b_unit_task.set('unit_task:X state:running type:?type')
        b_focus.set('start')
        print('********* on this part of the bomb I must cut blue then red')

    ## body of the unit task
    def X_cut_the_blue_wire(b_unit_task='unit_task:X state:running type:?type',
                          b_focus='start'):
        b_method.set('method:cut_wire target:blue_wire state:start')
        b_focus.set('cutting_blue_wire')
        ##print 'need to cut the blue wire'

    def X_cut_the_red_wire(b_method='state:finished',
                         b_unit_task='unit_task:X state:running type:?type',
                         b_focus='wire_is_cut'):
        b_method.set('method:cut_wire target:red_wire state:start')
        b_focus.set('done')
        b_unit_task.set('unit_task:X state:end type:?type')  ## this line ends the unit task
        ##print 'need to cut the red wire'

    ## finishing the unit task
    def X_finished_ordered(b_method='state:finished',
                           b_unit_task='unit_task:X state:end type:ordered'):
        ##print 'finished unit task X - ordered'
        b_unit_task.set('unit_task:X state:finished type:ordered')

    ## Y unit task
    ## This unit task represents a routine situation where the bomb technician must expose and cut,
    ## first a red wire then a blue wire

    ## these decide if the unit task will be run as part of a sequence of unit tasks 'ordered'
    ## OR as situated unit tasks determined by the environment 'unordered'
        
    def Y_unit_task_ordered(b_unit_task='unit_task:Y state:start type:ordered'):
        b_unit_task.set('unit_task:Y state:begin type:ordered')
        ##print 'start unit task Y ordered'

    ## the first production in the unit task must begin in this way
    def Y_start_unit_task(b_unit_task='unit_task:Y state:begin type:?type'):
        b_unit_task.set('unit_task:Y state:running type:?type')
        b_focus.set('start')
        print('********* on this part of the bomb I must cut red then blue')

    ## body of the unit task

    def Y_cut_the_red_wire(b_unit_task='unit_task:Y state:running type:?type',
                           b_focus='start'):
        b_method.set('method:cut_wire target:red_wire state:start')
        b_focus.set('cutting_red_wire')
        ##print 'need to cut the red wire'


    def Y_cut_the_blue_wire(b_method='state:finished',
                            b_unit_task='unit_task:Y state:running type:?type',
                            b_focus='wire_is_cut'):
        b_method.set('method:cut_wire target:blue_wire state:start')
        b_focus.set('done')
        b_unit_task.set('unit_task:Y state:end type:?type')  ## this line ends the unit task

        ##print 'need to cut the blue wire


    ## finishing the unit task
    def Y_finished_ordered(b_method='state:finished',
                           b_unit_task='unit_task:Y state:end type:ordered'):
        ##print 'finished unit task Y - ordered'
        b_unit_task.set('unit_task:Y state:finished type:ordered')


################ methods #######################

## cut wire method

    def expose_wire(b_method='method:cut_wire target:?target state:start'):  # target is the chunk to be altered
        motor.change_state(target, "exposed")
        b_method.set('method:cut_wire target:?target state:running')
        b_operator.set('operator:cut target:?target state:running')
        b_focus.set('expose_wire')
        print('expose wire')
        print('target object = ', target)

    def wire_exposed(b_method='method:?method target:?target state:running',
                     motor_finst='state:finished',
                     b_focus='expose_wire'):
        b_focus.set('change_state')
        motor.motor_finst_reset()
        print('I have exposed ', target)

    def cut_wire(b_method='method:cut_wire target:?target state:running',
                 b_focus='change_state'):  # target is the chunk to be altered
        motor.change_state(target, "cut")
        b_method.set('method:change_state target:?target state:running')
        b_operator.set('operator:cut target:?target state:running')
        b_focus.set('cutting_wire')
        print('cut wire')
        print('target object = ', target)

    def wire_cut(b_method='method:?method target:?target state:running',
                 motor_finst='state:finished',
                 b_focus='cutting_wire'):
        b_method.set('method:?method target:?target state:finished')
        motor.motor_finst_reset()
        b_focus.set('wire_is_cut')
        print('I have cut ', target)


################ explanations #######################

    def observer(b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running', b_context='finished:?planning_unit status:unoccupied', b_unit_task='observe'):
        motor.watchBomb(cue)
        b_unit_task.set('stop')
        b_context.set('finished:observing status:remembering')

#   Remember the current bomb state after acting - placeholder for episodic memory
    def memorize1(b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running', b_context='finished:observing status:remembering'):
        DM.request('object:bomb state:? time:1')
        b_context.set('finished:remembering status:memorizing')

#   Memorize what happened as an inference
    def memorizeDisarmed(b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running', b_context='finished:remembering status:memorizing', b_DM='object:bomb state:disarmed time:1'):
        DM.add('metainf:disarm object:bomb interv:?cue isthen:disarmed')
        b_context.set('finished:memorizing status:inferringDisarmed')
    def memorizeArmed(b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running', b_context='finished:remembering status:memorizing', b_DM='object:bomb state:armed time:1'):
        DM.add('metainf:arm object:bomb interv:?cue isthen:armed')
        b_context.set('finished:memorizing status:inferringArmed')

#   Infer counterfactual potential outcome
    def inferDisarmed(b_context='finished:memorizing status:inferringDisarmed', b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running'):
        DM.request('metainf:disarm object:bomb interv:?cue isthen:disarmed')
        b_context.set('finished:inferring status:metainferringDisarmed')
    def inferArmed(b_context='finished:memorizing status:inferringArmed', b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running'):
        DM.request('metainf:arm object:bomb interv:?cue isthen:armed')
        b_context.set('finished:inferring status:metainferringArmed')

    def metainfDisarmed(b_context='finished:inferring status:metainferringDisarmed', b_DM='metainf:disarm object:bomb interv:?cue isthen:disarmed'):
        DM.request('interv0:?cue interv1:? interv2:?')
        b_context.set('finished:metainferring status:counterfactingDisarmed')
    def metainfArmed(b_context='finished:inferring status:metainferringArmed', b_DM='metainf:arm object:bomb interv:?cue isthen:armed'):
        DM.request('interv0:?cue interv1:? interv2:?')
        b_context.set('finished:metainferring status:counterfactingArmed')

    def counterfactDisarmed(b_context='finished:metainferring status:counterfactingDisarmed', b_DM='interv0:?cue interv1:?interv1 interv2:?interv2'):
        DM.request('interv0:?interv3 interv1:?interv2 interv2:?interv1')
        b_context.set('finished:counterfacting status:metacounterArmed')
    def counterfactArmed(b_context='finished:metainferring status:counterfactingArmed', b_DM='interv0:?cue interv1:?interv1 interv2:?interv2'):
        DM.request('interv0:?interv3 interv1:?interv2 interv2:?interv1')
        b_context.set('finished:counterfacting status:metacounterDisarmed')

## We now flip the state... we know how to disar/arm it, so how do we arm/disarm it?
    def metaCounteraddArmed(b_context='finished:counterfacting status:metacounterArmed', b_DM='interv0:?interv3 interv1:?interv2 interv2:?interv1'):
        DM.add('metainf:arm object:bomb interv:?interv3 isthen:armed')
        b_context.set('finished:explanation status:unoccupiedArmed')
    def metaCounteraddDisarmed(b_context='finished:counterfacting status:metacounterDisarmed', b_DM='interv0:?interv3 interv1:?interv2 interv2:?interv1'):
        DM.add('metainf:disarm object:bomb interv:?interv3 isthen:disarmed')
        b_context.set('finished:explanation status:unoccupiedDisarmed')

    def answerTheInf(b_context='finished:explanation status:unoccupiedArmed'):
        print("How do you disarm the bomb?")
        DM.request('metainf:disarm object:bomb interv:?interv4 isthen:disarmed')
        b_context.set('finished:answerInf status:unoccupiedArmed')
    def reportInf(b_context='finished:answerInf status:unoccupiedArmed', b_DM='metainf:disarm object:bomb interv:?interv4 isthen:disarmed'):
        print(interv4)
        b_context.set('finished:reportInf status:unoccupiedArmed')

    def answerBadInf(b_context='finished:explanation status:unoccupiedDisarmed'):
        print("How do you leave the bomb armed?")
        DM.request('metainf:arm object:bomb interv:?interv4 isthen:armed')
        b_context.set('finished:answerInf status:unoccupiedDisarmed')
    def reportBadInf(b_context='finished:answerInf status:unoccupiedDisarmed', b_DM='metainf:arm object:bomb interv:?interv4 isthen:armed'):
        print(interv4)
        b_context.set('finished:reportInf status:unoccupiedDisarmed')

    def answerTheCounter(b_context='finished:reportInf status:unoccupiedArmed'):
        print("What plan would've left the bomb armed?")
        DM.request('metainf:arm object:bomb interv:?interv5 isthen:armed')
        b_context.set('finished:answerCounter status:unoccupiedArmed')
    def reportCounter(b_context='finished:answerCounter status:unoccupiedArmed', b_DM='metainf:arm object:bomb interv:?interv5 isthen:armed'):
        print(interv5)
        b_context.set('finished:reportCounter status:unoccupied')

    def answerInfCounter(b_context='finished:reportInf status:unoccupiedDisarmed'):
        print("What plan would've disarmed the bomb?")
        DM.request('metainf:disarm object:bomb interv:?interv5 isthen:disarmed')
        b_context.set('finished:answerCounter status:unoccupiedDisarmed')
    def reportInfCounter(b_context='finished:answerCounter status:unoccupiedDisarmed', b_DM='metainf:disarm object:bomb interv:?interv5 isthen:disarmed'):
        print(interv5)
        b_context.set('finished:reportCounter status:unoccupied')


############## run model #############

tim = MyAgent()  # name the agent
nakatomi = MyEnvironment()  # name the environment
nakatomi.agent = tim  # put the agent in the environment
ccm.log_everything(nakatomi)  # ##print out what happens in the environment
nakatomi.run()  # run the environment

ccm.finished()  # stop the environment

