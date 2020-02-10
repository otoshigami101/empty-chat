<?php

    namespace DB;

    class Connection{
        
        var $connection;

        public function __construct($host,$user,$pass,$db) {
            $this->connect($host,$user,$pass,$db);
        }
        
        protected function connect($host,$user,$pass,$db){
            $this->connection = mysqli_connect($host,$user,$pass,$db);

            if(!$this->connection){
                echo "FAILED TO CONNECT DATABASE : ".mysqli_connect_error();
                exit();
            }
        }

        public function statement($sql){
            if($result = $this->connection->query($sql)){
                return $result;
            }else{
                return "ERROR : ".mysqli_error($this->connection);
            }

            $this->connection->close();
        }
    }
    