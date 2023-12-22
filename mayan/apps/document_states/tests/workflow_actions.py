from ..classes import WorkflowAction


class WorkflowActionTest(WorkflowAction):
    label = 'test workflow state action'

    def execute(self, context):
        context['workflow_instance']._workflow_state_action_executed = True
