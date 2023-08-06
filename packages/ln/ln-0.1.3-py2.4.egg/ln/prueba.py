import ln

class Content(ln.Thing): pass

doc1 = Content('doc1')
ln.KB.tell(doc1)

class WfState(ln.Thing): pass

deleted = WfState('deleted')
ln.KB.tell(deleted)

private = WfState('private')
ln.KB.tell(private)

public = WfState('public')
ln.KB.tell(public)

class HasState(ln.State):
    subject = Content
    advs = {'state': WfState}

class ChangeOfState(ln.State):
    subject = Content
    advs = {'init_state': WfState, 'end_state': WfState}

class User(ln.Thing): pass

john = User('john')
ln.KB.tell(john)

class Action(ln.Thing): pass

view = Action('view')
ln.KB.tell(view)

edit = Action('edit')
ln.KB.tell(edit)

remove = Action('remove')
ln.KB.tell(remove)

change_state = Action('change_state')
ln.KB.tell(change_state)

class HasPermission(ln.State):
    subject = User
    advs = {'action': Action, 'content': Content}

class Do(ln.State):
    subject = User
    advs = {'action': Action, 'content': Content}

class Ask(ln.State):
    subject = User
    advs = {'action': Action, 'content': Content}

class IsNotifed(ln.State):
    subject = User
    advs = {'expr': ln.Prop}

class RelationToContent(ln.Thing): pass

owner = RelationToContent('owner')
ln.KB.tell(owner)

not_owner = RelationToContent('not_owner')
ln.KB.tell(not_owner)

class HasRelation(ln.State):
    subject = User
    advs = {'relation_to_content': RelationToContent,
            'content': Content}

prop1 = ln.Prop(doc1, HasState(state=public), 0)
ln.KB.tell(prop1)

u1 = User('X1')
c1 = Content('X2')
p1 = ln.Prop(c1, HasState(state=public), ln.Number('X3'))
p2 = ln.Prop(u1, HasPermission(action=view,content=c1),
                                            ln.Number('X3'))
ln.KB.tell(ln.Rule((u1, c1, p1),(p2,)))

ln.KB.extend()

ln.KB.ask(remove)

remove.name = 'delete'
ln.KB.ask(remove)

q1 = ln.Prop(s=john,
             v=HasPermission(action=view,content=doc1),
             t=0)
ln.KB.ask(q1)




# a content has-state public at time
# ->
# a user has-permission to view that content at that time
#
#
# a content has-state private/public at time
# a user has-relation owner to a content at time
# ->
# the user has-permission to view/edit/delete/change-state the content at time
#
#
# a user asks an action for a content at time
# the user has-permission for that action on that content at time
# ->
# the user do that action on that content at time











