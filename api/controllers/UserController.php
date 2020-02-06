<?php

namespace Controllers;

use Controllers\Controller as Controller;

class UserController extends Controller{
    public function fetchAll($except = null){
        $condition = $except?' where users.id <> '.$except:'';
        $user = $this->get('users',$condition)
        ->select([
            'id','name','username'
        ])->toArray();

        echo json_encode(['users'=>$user]);
    }
    public function fetch($id){
        $user = $this->get('users',' where id = '.$this->db->connection->real_escape_string($id))
        ->select([
            'id','name','username'
        ])->row();

        echo json_encode($user);
    }
}