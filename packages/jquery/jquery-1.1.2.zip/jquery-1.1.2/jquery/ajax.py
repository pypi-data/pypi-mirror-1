from turbogears.widgets import Widget
from widgets import jquery

class link_to_remote(Widget):
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
                },
                dataType: "html"
            });
            return false;
        });});
        </script>
    """
    params = ["target", "update", "href"]
    params_doc = {"target":"the link id",
                "update":"div to be replaced",
                "href":"remote method href",
                }

class periodically_call_remote(Widget):
    """
    periodically_call_remote
    
    default interval is 1000(ms)
    
    from pquery http://www.ngcoders.com/pquery/
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
                "interval":"update time interval"
                }
    interval = 1000
