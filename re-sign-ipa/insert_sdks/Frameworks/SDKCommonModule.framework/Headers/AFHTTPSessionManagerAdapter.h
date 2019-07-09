//
//  AFHTTPSessionManagerAdapter.h
//  SDKCommonModule
//
//  Created by star.liao on 2017/4/1.
//  Copyright © 2017年 com.idreamsky. All rights reserved.
//

#import <SDKCommonModule/SDKCommonModule.h>
#import "AFHTTPSessionManager.h"

@interface AFHTTPSessionManagerAdapter : AFHTTPSessionManager

+(AFHTTPSessionManager *)sharedManager;

@end
