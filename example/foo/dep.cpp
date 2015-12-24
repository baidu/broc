/***************************************************************************
 * 
 * Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
 * 
 **************************************************************************/
 
 
 
/**
 * @file example_dependency.cpp
 * @author liruihao(com@baidu.com)
 * @date 2015/12/07 16:07:40
 * @brief 
 *  
 **/

#include <stdio.h>

#include "brocbuild/function/src/function.h"

int main()
{
    function myfunction;
    printf("Hello world\nUse function module?\n%s\n", \
            myfunction.is_function()? "Yes": "No");
    return 0;
}
