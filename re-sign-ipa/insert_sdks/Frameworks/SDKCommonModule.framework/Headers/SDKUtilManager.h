//
//  SDKUtilManager.h
//  SDKCommonModule
//
//  Created by star.liao on 2017/4/1.
//  Copyright © 2017年 com.idreamsky. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "JSONModel.h"

@interface SDKUtilManager :JSONModel

//平台_手机品牌_屏幕尺寸_机型_客户端版本_系统版本_分辨率_网络类型_运营商_imei
@property(nonatomic,assign) int systemPlatform;
@property(nonatomic,strong) NSString* imei;//0.2.1是idfa
@property(nonatomic,strong) NSString* device_brand; // iphone5s
@property(nonatomic,strong) NSString* device_model; // iphone
@property(nonatomic,assign) int screenSize;
@property(nonatomic,strong) NSString* uuid;//0.2.1改为从休闲uuid取值,取不到值用idfv
@property(nonatomic,strong) NSString* systemVersion;
@property(nonatomic,strong) NSString* screenResolution;
@property(nonatomic,assign) int screentOrientation;
@property(nonatomic,strong) NSString* CFBundleIdentifier;
@property(nonatomic,strong) NSString* appVersion;
@property(nonatomic,strong) NSString* userAgent;
@property(nonatomic,strong) NSString* systemVersionNumber;

+(SDKUtilManager *)sharedManager;

@end
