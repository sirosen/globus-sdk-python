# test the `orderby` param for `FlowsClient.list_flows()`
# str or tuple, but the tuple's right value is validated (the left value is not)
import globus_sdk

fc = globus_sdk.FlowsClient()

# no params as a safety/sanity check
fc.list_flows()
# orderby as a string, any string (valid or not)
fc.list_flows(orderby="title DESC")
fc.list_flows(orderby="scope_string ASC")
fc.list_flows(orderby="title DESC ASC DESC")
fc.list_flows(orderby="scope_string")
fc.list_flows(orderby="frobulators INVERTED COROLLARY")

# orderby as a tuple, all the valid styles
# note that the field name isn't checked against a literal
fc.list_flows(orderby=("title", "DESC"))
fc.list_flows(orderby=("scope_string", "ASC"))
fc.list_flows(orderby=("title DESC ASC", "DESC"))
fc.list_flows(orderby=("frobulators", "ASC"))

# orderby as a tuple, but invalid odering -- type errors
fc.list_flows(orderby=("scope_string", "AGE"))  # type: ignore[arg-type]
fc.list_flows(orderby=("frobulator", "normcore_demuddler"))  # type: ignore[arg-type]

# and the tuple arity has to be right too
fc.list_flows(orderby=("frobulator",))  # type: ignore[arg-type]
fc.list_flows(orderby=("frobulator", "ASC", "ASC"))  # type: ignore[arg-type]
