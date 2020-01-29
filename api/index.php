<?php

require(__DIR__.'/api/controllers/*');

class API
{
    var $request;
    
    public function __construct($request) {
        $this->request = $request;
    }

    public function initialize()
    {
        switch($this->request){
            case '/login':
                $login = new Login;
                return $login->attempt($_POST);

                break;
            default:
                http_response_code('404');
                break;
        }
    }
}
$api = new API($_SERVER['REQUEST_URI']);
$api->initialize();