<?php

require('../database/connection.php');

class Controller
{
    var $db;

    public function __construct() {
        $this->db = new Connection('127.0.0.1','root','','empty-chat');
    }

    public function insert($table,$arrays){
        $sql = 'INSERT INTO '.$table.' SET ';
        $i = 0;

        foreach($arrays as $field => $val){
            $value = $this->db->connection->real_escape_string($val);
            if($i < (count($arrays)-1)){
                $sql .= $field .'='. $value.',';
            }else{
                $sql .= $field .'='. $value;
            }
            $i++;
        }

        $result = $this->db->statement($sql);
        
        if(is_string($result) and !strpos($result,'ERROR')){
            return $result;
            exit();
        }

        return 'success';
    }

    public function get($table,$condition = null){
        $wish = new class extends Controller{
            
            var $sql;
            var $table,$condition;
            
            function init($table,$condition) {
                $this->table = $table;
                $this->condition = $condition;
            }

            function toArray(){
                $this->sql = 'SELECT * FROM '.$this->table.' '.$this->condition;
                $result = $this->db->statement($this->sql);

                if(is_string($result) and !strpos($result,'ERROR')){
                    return $result;
                    exit();
                }

                return $result->fetch_array(MYSQLI_BOTH);
            }

            function row(){
                $this->sql = 'SELECT * FROM '.$this->table.' '.$this->condition.' limit 1';
                $result = $this->db->statement($this->sql);

                if(is_string($result) and !strpos($result,'ERROR')){
                    return $result;
                    exit();
                }

                return $result->fetch_assoc();
            }
        };
        
        $wish->init($table,$condition);

        return $wish;
    }
}
