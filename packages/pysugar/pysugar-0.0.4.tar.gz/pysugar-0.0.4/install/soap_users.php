<?php
 // This program is under the same license as the rest
 // of the PySugar distribution: PSF
 // Please read LICENSE for more information
 $GLOBALS['sugarEntry'] = true;

ob_start();
require_once('include/nusoap/nusoap.php');
require_once('modules/ACL/ACLController.php');


clean_special_arguments();

$GLOBALS['log'] =& LoggerManager::getLogger('SugarCRM');

// check for old config format.
if(empty($sugar_config) && isset($dbconfig['db_host_name']))
{
   make_sugar_config($sugar_config);
}

// Administration include
require_once('modules/Administration/Administration.php');
require_once('modules/Administration/updater_utils.php');

global $HTTP_RAW_POST_DATA;

$administrator = new Administration();
$administrator->retrieveSettings();

$timedate = new TimeDate();
// Temp should be in config.php
$NAMESPACE = 'http://www.sugarcrm.com/sugarcrm';
$server = new soap_server;
$server->configureWSDL('sugarsoap',
    $NAMESPACE,
    $sugar_config['site_url'].'/soap_users.php');

require_once('modules/ACLRoles/ACLRole.php');
require_once('modules/Users/User.php');

$server->wsdl->addComplexType(
    'create_user_result',
    'ComplexType',
    'struct',
    'all',
    '',
    array(
        'id' => array('name'=>'id', 'type'=>'xsd:string'),
        'error' => array('name'=>'Access Denied',
        'type'=>'tns:error_value')
    )
);

$server->wsdl->addComplexType(
    'ArrayOfstring',
    'complexType',
    'array',
    '',
    'SOAP-ENC:Array',
    array(),
    array(array('ref'=>'SOAP-ENC:arrayType',
    'wsdl:arrayType'=>'string[]')),
    'xsd:string'
);

$server->wsdl->addComplexType(
    'user_role_id_array',
    'ComplexType',
    'struct',
    'all',
    '',
    array(
        'role_ids' => array('name'=>'role_id',
        'type'=>'tns:ArrayOfstring'),

        'error' => array('name'=>'Access Denied',
        'type'=>'tns:error_value')
        )
    );

$server->register(
    'get_user_role_ids',
    array('session_id'=>'xsd:string', 'user_id'=>'xsd:string'),
    array('return'=>'tns:user_role_id_array'),
    $NAMESPACE);

$server->register(
    'create_user',
    array(
        'session_id'=>'xsd:string',
        'username'=>'xsd:string',
        'password'=>'xsd:string'),
    array(
        'return'=>'tns:create_user_result'),
    $NAMESPACE);

$server->register(
    'remove_user_role',
    array(
        'session_id'=>'xsd:string',
        'role_id'=>'xsd:string',
        'user_id'=>'xsd:string'),
    array('return'=>'xsd:int'),
    $NAMESPACE);

function remove_user_role($session_id, $role_id, $user_id)
{
    /** Remove the role from acl_roles_users table with
     *  acl_roles_users.role_id = role_id for the user (user_id)  **/
    $error = new SoapError();
    if(!validate_admin($session_id))
    {
        $error->set_error('no_access');
    }
    else
    {
        $db =& PearDatabase::getInstance();
        $query = "DELETE FROM acl_roles_users 
            WHERE role_id='$role_id'
            AND user_id='$user_id';";
        $result = $db->query($query);
    }
    return 0;
}


function get_user_role_ids($session_id, $user_id)
{
    /** Get all related role id for user (user_id) **/
    $error = new SoapError();
    if(!validate_admin($session_id))
    {
        $error->set_error('no_access');
    }
    else
    {
        $db =& PearDatabase::getInstance();
        $query = "SELECT acl_roles.*
            FROM acl_roles, acl_roles_users
            WHERE acl_roles_users.user_id = '$user_id'
            AND acl_roles.id = acl_roles_users.role_id
            AND acl_roles.deleted=0 
            ORDER BY name;";
        $result = $db->query($query);
        $user_roles = array();
        while($row = $db->fetchByAssoc($result) ){
            $role = new ACLRole();
            $role->populateFromRow($row);
            $user_roles[] = $role->id;
        }
    }
    return array('error'=>$error, 'role_ids'=>$user_roles);
}

function create_user($session_id, $username, $password)
{
    /* Create a sugar user,
     * return guid for the newly created object, or '-1' if error */
    $user_id = '-1';
    $error = new SoapError();
    if(!validate_admin($session_id))
    {
        $error->set_error('no_access');
    }
    else if(user_exist($username))
    {
        $error->set_error('duplicates');
    }
    else
    {
        $new_user = new User();
        $new_user->last_name = $username;
        $new_user->user_name = $username;
        $new_user->title = $username;
        $new_user->user_password = $new_user->
            encrypt_password($password);
        $new_user->user_hash = strtolower(md5($password));
        $new_user->is_admin = 'off';
        $new_user->status = 'Active';
        $new_user->email = '';
        $new_user->save();

        $user_id = $new_user->id;
        $error->set_error('None');
    }
    return array('id'=>$user_id, 'error'=>$error);
}

function user_exist($username)
{
    $user = new User();
    $user_id = $user->retrieve_user_id($username);
    return $user_id;
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
        if($current_user->is_admin == 'on')
		    return true;
        else
            return false;
	}
 }


require_once('soap/SoapSugarUsers.php');
require_once('soap/SoapData.php');
require_once('modules/ACLRoles/ACLRole.php');

/* Begin the HTTP listener service and exit. */
ob_clean();
$HTTP_RAW_POST_DATA = isset($HTTP_RAW_POST_DATA) ? $HTTP_RAW_POST_DATA : '';
$server->service($HTTP_RAW_POST_DATA);

ob_end_flush();
sugar_cleanup();
exit();
?>

