<?php

namespace Controllers;

use Controllers\Controller as Controller;
use \Firebase\JWT\JWT;

class AuthController extends Controller
{
    var $iss,$key;

    public function __construct(Type $var = null) {
        parent::__construct();
        $this->iss = "http://localhost:8081/login";
        $this->key = file_get_contents(__DIR__.'/../mykey.pem');
    }

    public function attempt_login($input)
    {

        $username = $this->db->connection->real_escape_string($input['username']);
        $password = $this->db->connection->real_escape_string($input['password']);
        
        $login = $this->get('users','where 
            username = "'.$username.'" and 
            password = "'.$password.'"')->row();

        if($login->id){
            $token = array(
                "iss" => $this->iss,
                'data' => [
                    'id' => $login->id,
                    'name' => $login->name,
                    'username' => $login->username,
                ],
            ); 

            $jwt = JWT::encode($token,$this->key);

            echo json_encode([
                'msg' => 'Successfull Login.',
                'jwt_token' => $jwt,
            ]);
            
        }else{
            echo json_encode(['msg' => 'Login Failed.']);
        }
    } 
    
    public function validate_login($input)
    {
        try{
            JWT::$timestamp = 0;
            $decode = JWT::decode($input['jwt_token'],$this->key, array('HS256'));
            
            echo json_encode([
                'msg' => 'Access granted.',
                'data' => $decode->data,
            ]);
        }catch(\Exception $e){
            
            http_response_code(401);

            echo json_encode([
                'msg' => 'Access Denied.',
                'error' => $e->getMessage(),
            ]);
        }
    }
}
