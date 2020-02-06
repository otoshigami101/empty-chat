<?php

require 'vendor/autoload.php';

header('Access-Control-Allow-Methods: *');
header('Access-Control-Allow-Headers: *');
header('Content-Type: application/json');

class API
{
    var $request,$method,$input;
    
    public function __construct($uri,$method) {
        $this->request = $uri;
        $this->method = $method;
        $this->input = json_decode(file_get_contents('php://input'), TRUE);
    }

    public function initialize()
    {    
        if($this->request == '/login'){
            header('Access-Control-Allow-Origin:  http://localhost:8080');

            if($this->input){
                $auth = new Controllers\AuthController;
                return $auth->attempt_login($this->input);
            }

        }elseif($this->request == '/validate_login'){
            header('Access-Control-Allow-Origin:  http://localhost:8080');

            if($this->input){
                $auth = new Controllers\AuthController;
                return $auth->validate_login($this->input);
            }
            
        }elseif($this->request == '/user'){
            header('Access-Control-Allow-Origin:  ws://localhost:4444');

            if($this->input){
                $user = new Controllers\UserController;
                return $user->show($this->input['id']);
            }
            
        }else{
            http_response_code(404);
        }
    }
}

$api = new API($_SERVER['REQUEST_URI'],$_SERVER['REQUEST_METHOD']);
$api->initialize();