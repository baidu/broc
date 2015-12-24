/***************************************************************************
 * 
 * Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
 * 
 **************************************************************************/
 
 
 
/**
 * @file example_ut_application.cpp
 * @author liruihao(com@baidu.com)
 * @date 2015/12/09 11:39:46
 * @brief 
 *  
 **/

#include <stdio.h>
#include <unistd.h>
#include <string>
#include <iostream>

int main(int argc, char *argv[])
{
    char ch;
    std::string outs = "";
    printf("Hello world!\n");
    while((ch = getopt(argc, argv, "c:h:")) != -1) {
        switch(ch) {
            case 'c': outs += "-c " + std::string(optarg) + " "; break;
            case 'h': outs += "-h " + std::string(optarg) + " "; break;
        }
    }
    printf("Args are :");
    std::cout << outs << std::endl;
    return 0;
}





















/* vim: set expandtab ts=4 sw=4 sts=4 tw=100: */
