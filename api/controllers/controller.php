<?php

namespace Controllers;

use DB\Connection as Connection;

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
                $sql .= $field .'= "'. $value.'",';
            }else{
                $sql .= $field .'= "'. $value.'"';
            }
            $i++;
        }

        $result = $this->db->statement($sql);
        
        if(is_string($result) and !strpos($result,'ERROR')){
            return $result.' SQL:'.$sql;
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
                    return $result.' SQL:'.$this->sql;
                    exit();
                }

                return (object)$result->fetch_array(MYSQLI_BOTH);
            }

            function row(){
                $this->sql = 'SELECT * FROM '.$this->table.' '.$this->condition.' limit 1';
                $result = $this->db->statement($this->sql);
                
                if(is_string($result) and !strpos($result,'ERROR')){
                    return $result.' SQL:'.$this->sql;
                    exit();
                }

                return (object)$result->fetch_assoc();
            }

            function select($fields){
                $columns = '';
                foreach($fields as $key => $field){
                    if($key < (count($fields)-1) and count($fields) > 1){
                        $columns .= $this->db->connection->real_escape_string($field) . ',';
                    }else{
                        $columns .= $this->db->connection->real_escape_string($field);
                    }
                }
                $this->sql = 'SELECT '.$columns.' FROM '.$this->table.' '.$this->condition;
                $result = $this->db->statement($this->sql);
                if(is_string($result) and !strpos($result,'ERROR')){
                    return $result.' SQL:'.$this->sql;
                    exit();
                }
                return new class($result){

                    public function __construct($result) {
                        $this->result = $result;
                    }
                    public function row()
                    {
                        return (object)$this->result->fetch_assoc();
                    }
                    public function toArray()
                    {
                        $result = [];
                        while($row = $this->result->fetch_array(MYSQLI_BOTH)){
                            $result[] = $row;
                        };

                        return $result;
                    }
                };
            }

            function count(){
                $this->sql = 'SELECT * FROM '.$this->table.' '.$this->condition.' limit 1';
                $result = $this->db->statement($this->sql);

                if(is_string($result) and !strpos($result,'ERROR')){
                    return $result.' SQL:'.$this->sql;
                    exit();
                }

                return (int)$result->num_rows;
            }
            
        };
        
        $wish->init($table,$condition);

        return $wish;
    }
    
    public function update($table,$arrays,$condition){
        $sql = 'UPDATE '.$table.' SET ';
        $i = 0;
        foreach($arrays as $field => $val){
            $value = $this->db->connection->real_escape_string($val);
            if($i < (count($arrays)-1)){
                $sql .= $field .'= "'. $value.'",';
            }else{
                $sql .= $field .'= "'. $value.'"';
            }
            $i++;
        }
        $sql .= ' WHERE '.$condition;

        $result = $this->db->statement($sql);
        
        if(is_string($result) and !strpos($result,'ERROR')){
            return $result.' SQL:'.$sql;
            exit();
        }
        
        return 'success';
    }
}
