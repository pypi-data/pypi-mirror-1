<?php
 // This program is under the same license as the rest
 // of the PySugar distribution: PSF
 // Please read LICENSE for more information

$server->register(
	'prune_meetings',
	array('session'=>'xsd:string', 'date_from'=>'xsd:string', 'date_to'=>'xsd:string'),
	array('return'=>'tns:set_entry_result'),
	$NAMESPACE);

function prune_meetings($session_id, $date_from, $date_to)
{
    $error = new SoapError();
    if(!validate_admin($session_id))
    {
        $error->set_error('no_access');
    }
    else
    {
        $db =& PearDatabase::getInstance();
        $query = "DELETE from meetings WHERE meetings.date_start >= '$date_from' and meetings.date_end <= '$date_to';";
        $result = $db->query($query);
        $error->set_error('no_error');
    }
    return array('id'=>session_id(), 'error'=>$error);
}

function validate_admin($session_id){
	/* test if the current session has administrative rights */
	/* if yes, returns True, else return False               */

	session_id($session_id);
	session_start();
	
    if(!empty($_SESSION['is_valid_session']) &&
        $_SESSION['ip_address'] == $_SERVER['REMOTE_ADDR'] &&
        $_SESSION['type'] == 'user'){
		
		global $current_user;
		require_once('modules/Users/User.php');
		$current_user = new User();
		$current_user->retrieve($_SESSION['user_id']);
        login_success();
        if($current_user->is_admin)
		    return true;
        else
            return false;
	}

	session_destroy();
	return false;
}

?>

