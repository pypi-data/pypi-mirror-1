Introduction
============

raptus.workflownotification provides a pluggable way to send notifications to 
predefined recipients on a workflow transition.

To enable notifications an adapter is registered providing the INotificationEnabled 
interface is registered for the desired content type, where the transitions method
returns a list of transitions on which notifications are to be sent.

To define default recipients for notifications an adapter is registered
providing the INotificationRecipientProvider interface. Those may be named by the desired
workflow name or by a combination of workflow name and transition name to allow
different recipients by transition or workflow.

To define a template for a notification register an adapter providing the
INotificationTemplateProvider interface, where the same naming convention as 
for the recipient provider applies.

The adapters for INotificationRecipientProvider are additiv, recipients are collected
from all registered adapter in the given context. For INotificationTemplateProvider
adapters the most precise adapter win:

1. named adapter with name [workflow_name].[transition_name]
2. named adapter with name [workflow_name]
3. unnamed adapter
