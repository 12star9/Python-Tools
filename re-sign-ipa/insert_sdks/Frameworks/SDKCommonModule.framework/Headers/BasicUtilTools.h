//
//  BasicUtilTools.h
//  SDKCommonModule
//
//  Created by star.liao on 2017/4/1.
//  Copyright © 2017年 com.idreamsky. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>


@interface BasicUtilTools : NSObject

+(void)clearCache:(NSString *)path;
/**
 *  初始化获取一些耗时的参数
 */
+(void) initBasicParas;

//获取当前屏幕的尺寸
+ (CGSize)fixedScreenSize;

//Generanl-Version
+(NSString*) appVersion;

//Generanl-Build
+(NSString*) CFBundleVersion;

//包体标识符
+(NSString*) CFBundleIdentifier;

+(BOOL) isNetEnable;

//网络类型 @"wifi",@"2G",@"3G", @"4G",@""
+(NSString*) getNetType;

//网络类型 1：wifi,2：2G,3:3G, 4：4G 0：未知
+(int) getNetTypeInt;

+(NSString*) getCarrierName;
//运营商; 1:联通,2:电信,3:移动,0:其他
+(int) getCarrierIntName;

+(NSString*) udid;

+(NSString*) uuid;

+(NSString*) idfv;

+(NSString*) idfa;

+(BOOL) isIphoneX;

+(NSString*) lang;

//获取iOS设备机型号
+ (NSString*)deviceVersion;

+(NSString*)generateCrypt_str:(NSMutableDictionary*)dictionary;

+(BOOL) isPortrait;

+(NSString *)getResolutionStr;

//获取iOS系统版本号，IOS9
+(NSString*)getSystemVersion;

+(NSString *)generateMD5Str:(NSString*)str;

//获取iOS设备品牌标示定义，@"1"=>iphone,@"8"=>ipad,@"9"=>ipod
+(NSString*) getDeviceDes;

+(NSString*)ledouUUID;

+(NSString*) getUA;

+ (float)getIOSVersion;

+ (NSString*)getIOSVersionStr;

+(NSString*) getNetWorkTypeStr;

+(NSUInteger) checkDeviceOrientation;

+(NSDate*) getDateFromTimestamp:(NSString*)timeStamp;

+(NSDate*) getBeijingDateFromTimestamp:(NSString*)timeStamp;

//获取当前时间-北京时间
+(NSDate*) getCurrentBeijingDate;

//获取当前服务端时间戳
+(NSString*) getCurrentServerTimeStamp:(NSString*)headerDateStr;

//获取当前服务端UTC时间
+(NSDate*) getCurrentServerUTCDate:(NSString*)headerDateStr;

//获取当前服务端时间-北京时间
+(NSDate*) getCurrentServerBeijingDate:(NSString*)headerDateStr;

//获取当前系统时间
+(NSDate*) getCurrentSystemUTCDate;

//获取两个时间戳的差值，返回值以毫秒为单位
+(NSString*)getDurationStartTime:(NSString*)startTime
                         endTime:(NSString*)endTime;

//获取两个时间戳的差值，所有值以毫秒为单位
+(NSString*)getHoweSecondsDurationStartTime:(NSString*)startTime
                                    endTime:(NSString*)endTime;

//获取当前系统时间戳,客户端可能会修改，需要结合差值做校对最后的值
+(NSString*) getCurrentSystemTimeStamp;

//获取当前网络时间时间戳
+ (NSString *)getCurrentInternetDateTimeStamp;

+(NSString*) getTimeStamp;

// 获取当前设备可用内存(单位：MB）
+ (double)getAvailableMemory;

// 获取当前任务所占用的内存（单位：MB）
+ (double)getUsedMemory;

+(NSString*) getMemoryUsePercent;

+(float) getCpuUsage;

+(int) getCpuUsagePercent;

// 获取当前设备空闲的存储空间（单位：MB）
+ (double)getDeviceFreeSpace;

// 获取当前设备总的存储空间（单位：MB）
+ (double)getDeviceTotalSize;

//获取当前的时间（单位：毫秒）
+ (long long)getDeviceCurrentTime;

+ (void)deletAllFileInFolder:(NSString*)folderPath;

+ (void)deletAllFile:(NSString*)folderPath;

+(UIInterfaceOrientation) getCurrentScreenOrientation;

//照片获取本地路径转换
+ (NSString *)getImagePath:(UIImage *)image url:(NSString*)url folderPath:(NSString*)folderPath;

@end
