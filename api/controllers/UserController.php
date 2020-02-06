<?php

namespace Controllers;

use Controllers\Controller as Controller;

class UserController extends Controller{
    public function show($id){
        $user = $this->get('users',' where id = '.$this->db->connection->real_escape_string($id))->row();

        echo json_encode($user);
    }
}