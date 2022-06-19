# Code for Product recommendations based on files in "Movie product data"
# @author: Johannes Wawra
# @version: 1.0.0 Sunday, 19th of June 2022
# @usedPythonVersion: 3.9.13:6de2ca5, May 17 2022, 16:36:42
# this code contains 2 functions in main function at bottom: 
# getBestProducts(), recommendedProductsInSession()
# The functions use 3 helping functions:
# insertUserListsIntoProducts(), findKeywords(), findRelatedProducts()
# the helping functions are written before each of the main functions using them.

from copy import deepcopy
from operator import index
from numpy import NaN
import pandas
from requests import session

# sums product Lists via match with linear ID 
# @userDataFrame: df to take data from
# @userID: index to read data from u-df
# @userColumn: column to read data from u-df
# @productDataframe: df to write data to 
# @insertColumn: column to sum data, should be initialized with 0
# no return value, because productDataframe contains generated data
def insertUserListsIntoProducts(userDataframe,userID,userColumn,productDataframe,insertColumn):
    products = userDataframe.at[userID,userColumn]
    productList = products.split(";")
    for product in productList:
          index = int(product)-1
          productDataframe.at[index,insertColumn] = productData.at[index,insertColumn] + 1

#generates Dataframe with most viewed and best rated Products
# @userDataframe:df to read user data from
# @productDataframe:df to read movie data from
# @showData: shows top 5 product info
# @doSave: saves reduced top 5 product info
# @savePath: Path to save top 5 reduced list as csv
# @return: complete best product list
def getBestProducts(userDataframe, productDataframe, showData, doSave, savePath):
  #add columns for the view statistics into movie list
  productDataframe["views"] = 0
  productDataframe["purchases"] = 0
  #insert user statistics in movie list
  for userID in userDataframe.index:
    insertUserListsIntoProducts(userDataframe,userID,"viewed",productDataframe,"views")
    insertUserListsIntoProducts(userDataframe,userID,"purchased",productDataframe,"purchases")

  #sort generated data
  bestProductData = productDataframe.sort_values(["purchases","rating"], ascending=[False,False])
  
  #reduce generated data
  out = bestProductData.drop(bestProductData.loc[:,"year":"keyword5"].columns, axis = 1)
  out = out.iloc[0:5]
  if(showData):
  #show reduced data
    print(out.to_string(index = False))
  else:
    print("Showing Data disabled.")

  if(doSave):
    out.to_csv(savePath, sep=",", index = False, header = None)
    print("Data was saved to: " + savePath)
  else:
    print("Saving disabled.")
  return bestProductData




# @productDataframe: df to read keywords from
# @productIndex: index in df to read keywords from
# @return: all 5 keywords as list
def findKeywords(productDataframe, productIndex):
  keywordList = []
  for keyword_index in range (1,6):
    keywordName = "keyword" + str(keyword_index)
    keyword = productDataframe.at[productIndex,keywordName]
    if not (keyword == ' '):  
      keywordList.append(keyword)
  return keywordList

# sums up matches from keywords and returns top 5 matched products
# @keywordList: keywords to match
# @productDataFrame: df to search for matching keywords
# @excludeProductIndex: this product should not be included, because it would have highest match because it is identical
# @showData: True if matching entries shall be show
# @return: df with top 5 matched products from productDataframe
def findRelatedProducts (keywordList, productDataframe, excludeProductIndex, showData):
    for productIndex in productDataframe.index:
      #exclude same product, because it would have highest match
      if not(productIndex == excludeProductIndex):
        match = 0
        foundKeywords = findKeywords(productDataframe, productIndex)
        #countMatchingKeywords
        for keyword in keywordList:
            if keyword in foundKeywords:
              match += 1
        productDataframe.at[productIndex,"matchFactor"] = match
        

    #sortFoundProducts and take top 5 
    bestProducts = productDataframe.sort_values("matchFactor", ascending = False) 
    out = bestProducts.iloc[0:5] 
    if(showData):
      print("Seen Movie:")
      data = productDataframe.iloc[excludeProductIndex:excludeProductIndex+1]
      print(data.to_string(index = False))
      print("Related Movies:")
      print(out.to_string(index = False))
    return out


# calculates top 5 related Products relating to keywords of products
# @userSessionDataframe: contains products for which related products shall be found
# @userDataframe: used for showing Names in printout if not anonymous
# @productDataframe: contains all products and keywords
# @showData: True shows searched and related Products
# @anonymous: False shows user names, if Data is showed and saves userSessionDataframe without userID
# @doSave: saves top 5 recommended products in similar list to userSessionDataframe, extended to ";" separated recommendations
# @savePath: Path to save data to
# @return: userSessionDataframe with updated related Products to productID
def recommendedProductsInSession(userSessionDataframe, userDataFrame, productDataframe, showData, anonymous, doSave, savePath):
  recommendedSession = deepcopy(userSessionDataframe)
  if not(showData):
          print("Showing Data disabled.")
  for userID in userSessionDataframe.index:
    #add columns for the view statistics into movie list
    productDataframe["matchFactor"] = NaN
    #get keywords to search
    productID = userSessionDataframe.at[userID,"productID"]
    productIndex = productID - 1
    productKeywords = findKeywords(productDataframe, productIndex)
    
    #search related Products
    bestProducts = deepcopy(productDataframe)
    #showUserName
    if (not anonymous and showData):
      userIndex = userID - 1
      userName = userDataFrame.at[userIndex,"name"]
      print("User: " + userName)
    #calculate top 5 best related products
    bestProducts = findRelatedProducts(productKeywords, bestProducts, productIndex, showData)

    #save top 5 recommended movies in file with same structure as userSessions extended to recommendations as ";" separated string
    if(doSave):
      recommendedProductsList = []
      for product in bestProducts.index:
        recommendedProductsList.append(bestProducts.at[product,"ID"])
      recommendedProductsString = ";".join(map(str,recommendedProductsList))
      recommendedSession.at[userID,"recommendedProducts"] = recommendedProductsString
  if(doSave):
    if(anonymous):
      print("Anonymous saving of recommended movies.")
      recommendedSession.to_csv(savePath, sep=",", index = False, header = False)
    else:
      print("Saving with UserID.")
      recommendedSession.to_csv(savePath, sep=",", header = False)
    print("Data was saved to: " + savePath)
  else:
    print("Saving disabled")
  return recommendedSession




# Main function

#import all necessary data
userData = pandas.read_csv("Movie product data\\Users.txt", sep=",", header=None,
  names=["ID","name", "viewed", "purchased"])

productData = pandas.read_csv("Movie product data\\Products.txt", sep=",", header=None,
  names=["ID","name", "year", "keyword1", "keyword2", "keyword3", "keyword4", "keyword5", 
         "rating", "price"])

userSessionData = pandas.read_csv("Movie product data\\CurrentUserSession.txt", sep=",", header=None,
  names=["productID","recommendedProducts"])

#calculates most viewed and highest ranking movies
print("Calculating most viewed Movies...")
#boolean1: showData, boolean2: saveData
getBestProducts(userData, productData, True, False, "Movie product data\\bestProducts.txt", )
print("Done. \r\n")

#calculates top 5 related products
print("Calculating recommended Movies for Usersessions...")
#boolean1: showData, boolean2: anonymous, boolean3: saveData
#anonymous should be false, if userID should not be lost
recommendedProductsInSession(userSessionData, userData, productData, False, False, True, "Movie product data\\CurrentUserSession.txt")
print("Done.")