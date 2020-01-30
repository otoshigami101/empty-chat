<?php

class Chat{
    
    var $host,$port,$socket;

    public function __construct($host,$port) {
        $this->host = $host;
        $this->port = $port;
        
        $this->connect();
    }

    public function connect()
    {
        $this->socket = socket_create(AF_INET,SOCK_STREAM,getprotobyname('tcp'));
        socket_bind($socket,$this->host,$this->port);
        socket_listen($this->socket,1);
    }

    public function run()
    {
        echo "Waiting Incoming Connection ...";

        while(true)
            try{
                if(($newc = socket_accept($this->socket)) !== false)
                {
                    echo "Client $newc has connected\n";
                }
            }catch(\Exception $e){
                echo "ERROR :".$e;
            }
    }
}