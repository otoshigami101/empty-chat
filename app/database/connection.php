<?php
    class Connection{
        
        var $mysqli;

        public function __construct($host,$user,$pass,$db) {
            $this->connect($host,$user,$pass,$db);
        }
        
        protected function connect($host,$user,$pass,$db){
            $this->mysqli = mysqli_connect($host,$user,$pass,$db);

            if(!$this->mysqli){
                echo "FAILED TO CONNECT : ".mysqli_connect_error();
                exit();
            }
        }
    }

    new Connection('127.0.0.1','root','','empty-chat');
    