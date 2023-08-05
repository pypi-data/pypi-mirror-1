from turbogears.widgets import Widget
from widgets import jquery


"""
<p><strong>form_remote_tag</strong> - Ajax form submission.</p>
<p><form class="desc" action="ajax"  method="get" >
Field : <input type="text" name="field" /><br />
<input type="submit" /> 
</form>
</p>
<div id="idtoupdate">Update ME(Ajax form)</div>
${addFormback(target="formdesc", update="idtoupdate", href="ajax")}
"""

class FormRemote(Widget):
    """
    form_remote_tag is an ajax helper

    While target link is clicked, submit form in json format

    """
    name = "form_remote_tag"
    javascript = [jquery]
    template = """
        <script type="text/javascript">
        $(function(){$('form.${target}').submit(function(){ 
            alert("call fuc");
            $.ajax({url: "${href}",
            data: $(this.elements).serialize(), 
            success: function(response){
                $("#${update}").html(response);
                },
                dataType: "html"}); return false;
            });
        }); 
        </script>
    """
    params = ["target", "update", "href"]
    params_doc = {"target":"the link id",
                "update":"div to be replaced",
                "href":"remote method href",
                }
    

form_remote_tag = FormRemote()

class LinkRemote(Widget):
    """
    link_to_remote is an ajax helper

    While target link is clicked,
    use XMLHttpRequest to get a response from a remote method

    this widget has no call back.
    """
    name = "link_to_remote"
    javascript = [jquery]
    template = """
        <script type="text/javascript">
        $(function(){$('#${target}').click(function(){
            $.ajax({url: "${href}",
                success: function(response){
                    $("#${update}").html(response);
                    ${callback}
                },
                dataType: "html"
            });
            return false;
        });});
        </script>
    """
    params = ["target", "update", "href", "callback"]
    params_doc = {"target":"the link id",
                "update":"div to be replaced",
                "href":"remote method href",
                "callback":"call back functions, default is Null"
                }
    callback= ''

link_to_remote = LinkRemote()

class PeriodicallyCallRemote(Widget):
    """
    periodically_call_remote  is an ajax helper

    Fetch data from server periodically
    """
    name = "periodically_call_remote"
    javascript = [jquery]
    template = """
        <script type="text/javascript">
        $(document).ready(function() {
            setInterval(function() {
                $.ajax({url: "${href}",
                    success: function(response){
                        $("#${update}").html(response);
                    },
                    dataType: "html"
                })
            },${interval})
        });
        </script>
    """
    params = ["update", "href", "interval"]
    params_doc = {"update":"div to be replaced",
                "href":"remote method href",
                "interval":"update time interval, default is 1000(ms)"
                }
    interval = 1000


periodically_call_remote = PeriodicallyCallRemote

addCallback = link_to_remote
addFormback = form_remote_tag
addPeriodback = periodically_call_remote