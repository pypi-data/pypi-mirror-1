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
    <script type="text/javascript">
    <![CDATA[
        var approve_url = '${approve_url}';
        var reject_url = '${reject_url}';
        
        function approve() {
            $('vote_form').action = approve_url;
            form_container_window.showCenter(true);
        }
        
        function reject() {
            $('vote_form').action = reject_url;
            form_container_window.showCenter(true);
        }
    ]]>
    </script>
</head>

<body>
    <div id="form_container" style="display: none;">
        <form method="post" id="vote_form">
            <fieldset>
            <legend>Please enter a comment</legend>
            <textarea name="comment" rows="10" cols="60"></textarea><br/>
            <input type="submit" />
            </fieldset>
        </form>
    </div>
    
    ${window.display(dom_id="form_container")}
    
    <h2 py:if="state.instance_id">
        <div>${G_('Pending Modification For:')}</div>
        ${state.model_name} ID ${state.instance_id}<br/>
        ${unicode(state.get_object())}
    </h2>
    
    <h2 py:if="not state.instance_id">
        <span>${G_('New')}</span>
        <span>${state.model_name}</span>
    </h2>
    
    <div class="clearfix" style="font-weight: bold; font-size: larger">
        <div style="float: left;">
            <span>${G_('State ID:')}</span>
            <span>${state.id}</span>
        </div>
        <div style="float: right;">
            <span>${G_('User:')}</span>
            <span>${unicode(state.user)}</span>
        </div>
    </div>
    
    <div class="comment" style="font-weight: bold; font-size: larger" 
         py:if="state.comment">
         <span>${G_('Comment:')}</span>
         <span>${state.comment}</span>
    </div>
    
    ${panel.display(state.data)}
    
    <table py:if="state.pending and not state.rejected and state.can_authorize()" class="auth_panel">
        <tr>
            <td>
                <div class="auth_link">
                    <a href="javascript:approve()">
                        <img src="/tg_widgets/${images_dir}/check.gif" />
                        ${G_('Approve')}
                    </a>
                </div>
            </td>
            <td>
                <div class="auth_link">
                    <a href="javascript:reject()">
                        <img src="/tg_widgets/${images_dir}/cross.gif" />
                        ${G_('Reject')}
                    </a>
                </div>
            </td>
        </tr>
    </table>
</body>

</html>