//
//  AdsHttpOperationManager.h
//  SDKCommonModule
//
//  Created by star.liao on 2017/4/1.
//  Copyright © 2017年 com.idreamsky. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol SDKHttpRequestDelegate <NSObject>

@optional

-(void) requestResult:(id) responseObject withUrl:(NSString *)url;

-(void) requestResult:(id) responseObject withUrl:(NSString *)url withHttpBody:(NSString *)httpBody timedifference:(long long)timedifference;

-(void) requestResult:(id) responseObject withUrl:(NSString *)url withHttpBody:(NSString *)httpBody;


@end

@interface SDKHttpOperationManager : NSObject

@property(nonatomic,strong) NSString* requestURL;
@property(nonatomic,weak) id<SDKHttpRequestDelegate> delegate;
@property(nonatomic,strong) NSString* userAgent;
@property(nonatomic,assign) NSTimeInterval timeout;
@property(nonatomic,assign) int retryCount;
@property(nonatomic,strong) NSDictionary* headers;

+ (id)requestWithURL:(NSString *)newURL;

/**
 *  get请求
 */
-(void) requestData;

/**
 *  post请求
 *
 *  @param bodyStr post字符串
 */
-(void) postStringBody:(NSString *)bodyStr;

@end
