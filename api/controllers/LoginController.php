<?php

namespace Login;

require('controller.php');
class LoginController extends Controller
{
    public function attempt($request)
    {

        session_start();

        $username = $this->db->connection->real_escape_string($request['username']);
        $password = $this->db->connection->real_escape_string($request['password']);

        $login = $this->get('users','where 
            username = "'.$username.'" and 
            password = "'.$password.'"')->row();
        
        return $login;
    }    
}
