<?php
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: config_tests.py.example 5417 2007-11-22 10:01:48Z nilo $

$token = $_GET["token"];

if (isset($token))
    echo $token;
else
    echo "There was no Token submitted.";
?>
