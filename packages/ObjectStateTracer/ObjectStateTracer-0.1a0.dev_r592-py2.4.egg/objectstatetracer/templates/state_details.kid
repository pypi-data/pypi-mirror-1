<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">

<head>
    <title>State ${state.id} Details</title>
    <style type="text/css">
        .auth_panel {
            width: 20em;
            margin-left: auto;
            margin-right: auto;
            margin-top: 0.5em;
        }
        
        .auth_panel .auth_link {
            width: 10em;
            text-align: center;
        }
        
        .auth_panel .auth_link a {
            font-size: larger;
            text-decoration: none;
        }
        
        .auth_panel .auth_link img {
            border: 0em;
            vertical-align: middle;
        }
        
        .clearfix:after {
            content: "."; 
            display: block; 
            height: 0; 
            clear: both; 
            visibility: hidden;
        }
        
        .clearfix {display: inline-block;}
        
        /* Hides from IE-mac \*/
        * html .clearfix {height: 1%;}
        .clearfix {display: block;}
        /* End hide from IE-mac */
    </style>
</head>

<body>
    <h2 py:if="state.instance_id">
        Pending Modification For:<br/>
        ${state.model_name} ID ${state.instance_id}<br/>
        ${unicode(state.get_object())}
    </h2>
    <h2 py:if="not state.instance_id">
        New ${state.model_name}
    </h2>
    
    <div class="clearfix" style="font-weight: bold; font-size: larger">
        <div style="float: left;">State ID: ${state.id}</div>
        <div style="float: right;">User: ${unicode(state.user)}</div>
    </div>
    
    ${panel.display(state.data)}
    
    <table py:if="state.pending and not state.rejected" class="auth_panel">
        <tr>
            <td>
                <div class="auth_link">
                    <a href="${approve_url}">
                        <img src="/tg_widgets/${images_dir}/check.gif" />
                        Approve
                    </a>
                </div>
            </td>
            <td>
                <div class="auth_link">
                    <a href="${reject_url}">
                        <img src="/tg_widgets/${images_dir}/cross.gif" />
                        Reject
                    </a>
                </div>
            </td>
        </tr>
    </table>
</body>

</html>