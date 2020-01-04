# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 18:09:51 2018

@author: Soren Mortvedt
"""

import json

# Include Flask packages
from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin

import copy
import pymysql
import json
#import SimpleBO

# The main program that executes. This call creates an instance of a
# class and the constructor starts the runtime.
app = Flask(__name__)
#CORS(app)

def getBody():
    if request.data:
        body = json.loads(request.data)
    else:
        body = None
    return body

def parseArgs():
    query={}
    fields={}
    inArgs = None
    if request.args is not None:
        inArgs = dict(copy.copy(request.args))
    for k,v in inArgs.items():
            if k == "fields":
                fields = inArgs[k]
            elif k != "offset" and k != "limit" :
                query.update({k:v})
    return fields,query
    
def find_by_template(table, t, fields=None,lim=None,offs=None):
        cnx = pymysql.connect(host='localhost',
                          user='dbuser',
                          password='dbuser',
                          db='baseball',
                          charset='utf8mb4',
                          cursorclass=pymysql.cursors.DictCursor,
                          autocommit=True)
        cursor = cnx.cursor()
        if fields is not None:
            fieldsString=""
            for item in fields:
                if fieldsString == "":
                    fieldsString = item
                else:
                    fieldsString = fieldsString + ", " + item
        else:
            fieldsString = "*"

        keyValuePair = ""
        for k,v in t.items():
            if type(v) is list:
                if keyValuePair == "":
                    keyValuePair = k + "="+"\""+v[0]+"\""
                else:
                    keyValuePair = keyValuePair + "and " + k + "="+"\""+v[0]+"\""
            else:
                if keyValuePair == "":
                    keyValuePair = k + "="+"\""+v+"\""
                else:
                    keyValuePair = keyValuePair + "and " + k + "="+"\""+v+"\""
        links={}
        if lim==None and offs==None:
            q = "SELECT " + fieldsString+ " from "+table+" where "+keyValuePair+";"
            try:
                cursor.execute(q)
                results=cursor.fetchall()
            except Exception:
                return [],{}
        elif offs==None:
            q = "SELECT " + fieldsString+ " from "+table+" where "+keyValuePair+" LIMIT "+lim+";"
            try:
                cursor.execute(q)
                results=cursor.fetchall()
            except Exception:
                return [],{}
        elif lim==None:
            q = "SELECT " + fieldsString+ " from "+table+" where "+keyValuePair+" OFFSET "+offs+";"
            try:
                cursor.execute(q)
                results=cursor.fetchall()
            except Exception:
                return [],{}
        else:
            q = "SELECT SQL_CALC_FOUND_ROWS " + fieldsString+ " from "+table+" where "+keyValuePair+" LIMIT "+lim+" OFFSET "+offs+";"
            try:
                cursor.execute(q)
                results=cursor.fetchall()
            except Exception:
                return [],{}
            q = "Select FOUND_ROWS();"
            try:
                cursor.execute(q)
                totalLength=cursor.fetchall()
            except Exception as e:
                return [],{}
            totalLength = int(totalLength[0]["FOUND_ROWS()"])
            base=request.base_url
            query=dict(copy.copy(request.args))
            urlString=base
            otherQueries=False
            for k,v in query.items():
                if k.lower() != "offset" and k.lower() != "limit" :
                    otherQueries=True
                    if urlString == base:
                        urlString=urlString+"?"+ k+"="+', '.join(v)
                    else:
                        urlString=urlString+"&"+ k+"="+', '.join(v)
            if otherQueries:
                links["current:"] = urlString + "&offset="+offs+"&limit="+lim
                if totalLength>int(offs)+int(lim):
                    newOffs=str(int(offs)+int(lim))
                    links["next:"] = urlString + "&offset="+newOffs+"&limit="+lim
                newOffs=str(int(offs)-int(lim))
                if int(newOffs)>=0:
                    links["previous:"] = urlString + "&offset="+newOffs+"&limit="+lim
            else:
                links["current:"] = urlString + "?&offset="+offs+"&limit="+lim
                if totalLength>int(offs)+int(lim):
                    newOffs=str(int(offs)+int(lim))
                    links["next:"] = urlString + "?&offset="+newOffs+"&limit="+lim
                newOffs=str(int(offs)-int(lim))
                if int(newOffs)>=0:
                    links["previous:"] = urlString + "?&offset="+newOffs+"&limit="+lim
        
        if lim == None and len(results)<10:
            links={}
        return results,links
    
def getPrimaryKeyColumns(table):
    cnx = pymysql.connect(host='localhost',
                          user='dbuser',
                          password='dbuser',
                          db='baseball',
                          charset='utf8mb4',
                          cursorclass=pymysql.cursors.DictCursor,
                          autocommit=True)
    cursor = cnx.cursor()
    q= "SHOW index FROM lahman2017raw."+table+" WHERE Key_name = 'PRIMARY'"
    try:
        cursor.execute(q)
        results=cursor.fetchall()
    except Exception:
        return []
    columnNames = []
    for item in results:
        columnNames.append(item["Column_name"])
    return columnNames

def insert(table,r):
    cnx = pymysql.connect(host='localhost',
                          user='dbuser',
                          password='dbuser',
                          db='baseball',
                          charset='utf8mb4',
                          cursorclass=pymysql.cursors.DictCursor,
                          autocommit=True)
    cursor=cnx.cursor()
    keyString=""
    valueString=""
    for k,v in r.items():
        if keyString == "":
            keyString = k
        else:
            keyString = keyString + "," + k
        if valueString == "":
            valueString = "\""+v+"\""
        else:
            valueString = valueString + "," + "\"" + v +"\""
    q="INSERT INTO "+ table +" ("+ keyString +") VALUES("+ valueString +");"
    try:    
        cursor.execute(q)
    except Exception as e:
        return e
    
def update(table,updateValues,primaryKey):
    cnx = pymysql.connect(host='localhost',
                          user='dbuser',
                          password='dbuser',
                          db='baseball',
                          charset='utf8mb4',
                          cursorclass=pymysql.cursors.DictCursor,
                          autocommit=True)
    cursor=cnx.cursor()
    setString=""
    whereClause=""
    for k,v in updateValues.items():
        if setString == "":
            setString = k + " = '" + v+"'"
        else:
            setString = setString + ", " +  k + " = '" + v+"'"
    for k,v in primaryKey.items():
        if whereClause == "":
            whereClause = k + " = '" + v + "'"
        else:
            whereClause = whereClause + "AND " + k + " = '" + v +"'"
    q="Update "+ table +" SET "+ setString +" WHERE "+ whereClause +";"
    try:    
        cursor.execute(q)
    except Exception as e:
        return e
    
def delete(table, r):
    cnx = pymysql.connect(host='localhost',
                          user='dbuser',
                          password='dbuser',
                          db='baseball',
                          charset='utf8mb4',
                          cursorclass=pymysql.cursors.DictCursor,
                          autocommit=True)
    cursor=cnx.cursor()
    keyValueString = ""
    for k,v in r.items():
        if keyValueString == "":
            keyValueString = k + "="+"\""+v+"\""
        else:
            keyValueString = keyValueString + " and " + k + "="+"\""+v+"\""
    q="DELETE FROM "+table+" WHERE "+keyValueString+";"
    try:    
        cursor.execute(q)
    except Exception as e:
        return e

def getForeignKeys(table1, table2):
    cnx = pymysql.connect(host='localhost',
                          user='dbuser',
                          password='dbuser',
                          db='baseball',
                          charset='utf8mb4',
                          cursorclass=pymysql.cursors.DictCursor,
                          autocommit=True)
    cursor = cnx.cursor()
    q= "select constraint_schema as s_schema, constraint_name as c_name, table_name as s_table, \
        column_name as s_col_name, ordinal_position as o_position, position_in_unique_constraint as u_position, \
        referenced_table_schema as r_schema, referenced_table_name as r_table, referenced_column_name as r_column \
        from information_schema.KEY_COLUMN_USAGE \
        WHERE CONSTRAINT_SCHEMA = 'lahman2017raw' \
        and (table_name = '"+table1+"' or referenced_table_name = '"+table1+"')";

    try:
        cursor.execute(q)
        results=cursor.fetchall()
    except Exception:
        return []
    foreignKeys = []

    for item in results:
        if  item["r_table"] is not None:
            if table2.lower() == item["r_table"].lower():
                foreignKeys.append(item)
        if item["s_table"] is not None:
            if table2.lower() == item["s_table"].lower():
                foreignKeys.append(item)

    return foreignKeys

def getLimitOffset(query):
    inArgs = None
    offset=str(0)
    limit=str(10)
    if request.args is not None:
        inArgs = dict(copy.copy(request.args))
    for k,v in inArgs.items():
        if k.lower() == "offset":
            offset = inArgs[k]
        if k.lower() == "limit":
            limit = inArgs[k]
    return limit,offset

@app.route('/api/<resource>/<primaryKeyValues>/<relatedResource>', methods = ["GET", "POST"])
def get_related_resource(resource,primaryKeyValues,relatedResource):
    resource=resource.lower()
    relatedResource=relatedResource.lower()
    primaryKeyValues=primaryKeyValues.split("_")
    primaryColumns = getPrimaryKeyColumns(resource)
    resourceTemplateToFind = dict(zip(primaryColumns, primaryKeyValues))
    if len(primaryColumns) != len(primaryKeyValues):
        print("Cannot Query: Expecting "+ str(len(primaryColumns)) + " primary key elements, received " + str(len(primaryKeyValues))+".")
        return "Cannot Query: Expecting "+ str(len(primaryColumns)) + " primary key elements, received " + str(len(primaryKeyValues))+".", 404, {'Content-Type': 'application/json; charset=utf-8'}
    resourceResults,l = find_by_template(resource,resourceTemplateToFind)
    if not resourceResults:
        print("Invalid Primary Keys for table "+resource)
        return "Invalid Primary Keys for table "+resource, 404, {'Content-Type': 'application/json; charset=utf-8'}
    resourceResults = dict((k.lower(), v) for k,v in resourceResults[0].items()) # Get foreign keys spat out lower case column names for some reason...
    fields,query = parseArgs()
    limit,offset=getLimitOffset(query)
    fKeys = getForeignKeys(resource,relatedResource)
    if not fKeys:
        print("Could not find a relation between the tables")
        return "Could not find a relation between the tables", 404, {'Content-Type': 'application/json; charset=utf-8'}
    relatedResourcefKeyColumns=[]
    relatedResourcefKeyValues=[]
    for fkey in fKeys:
        if relatedResource == fkey['s_table']: #if the related resource does not contain the key, then the foreign key column must be in the r_table
            relatedResourcefKeyColumns.append(fkey['s_col_name'])
            resourceColumn = fkey['r_column'].lower()
            resourceValueToFind = resourceResults[resourceColumn]
            relatedResourcefKeyValues.append(resourceValueToFind)
        elif relatedResource == fkey['r_table']:
            relatedResourcefKeyColumns.append(fkey['r_column'])
            resourceColumn = fkey['s_col_name'].lower()
            resourceValueToFind = resourceResults[resourceColumn]
            relatedResourcefKeyValues.append(resourceValueToFind)
    
    if request.method == "GET":
        relatedResourceTemplateToFind= dict(zip(relatedResourcefKeyColumns, relatedResourcefKeyValues))
        if query:
            relatedResourceTemplateToFind.update(query)
        if not fields:
            relatedResourceResults,links = find_by_template(relatedResource,relatedResourceTemplateToFind,lim=limit,offs=offset)
        else:
            relatedResourceResults,links = find_by_template(relatedResource,relatedResourceTemplateToFind,fields,lim=limit,offs=offset)
        if relatedResourceResults:
            print(json.dumps(relatedResourceResults, indent=2))
            if links:
                print(json.dumps(links, indent=2))
                return json.dumps(relatedResourceResults, indent=2)+json.dumps(links, indent=2), 200, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return json.dumps(relatedResourceResults, indent=2), 200, {'Content-Type': 'application/json; charset=utf-8'}
        else:
            print("Could Not Find Results")
            return "Could Not Find Results", 404, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == "POST":
        relatedResourceTemplateToInclude= dict(zip(relatedResourcefKeyColumns, relatedResourcefKeyValues))
        body=getBody()
        relatedResourceTemplateToInclude.update(body)
        error = insert(relatedResource,relatedResourceTemplateToInclude)
        splitError = str(error).split(',')
        if splitError[0] == "(1364":
            print("Cannot insert into table, missing some primary keys ")
            return "Cannot insert into table, missing some primary keys ", 404, {'Content-Type': 'application/json; charset=utf-8'}
        elif splitError[0] == "(1054":
            print("Cannot insert into table, body contains rows not in table: "+str(error))
            return "Cannot insert into table, body contains rows not in table: "+str(error), 404, {'Content-Type': 'application/json; charset=utf-8'}
        elif error is None:
            print("Inserted")
            return "Inserted", 200, {'Content-Type': 'application/json; charset=utf-8'}
        else:
            print("Cannot insert into table, found error: "+ str(error))
            return "Cannot insert into table, found error: "+ str(error), 404, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        print("Method " + request.method + " on resource " + resource +"/"+ primaryKeyValues+ \
              "/"+ relatedResource+ " not implemented")
        return "Method " + request.method + " on resource " + resource +"/"+ primaryKeyValues+ \
              "/"+ relatedResource+ " not implemented",501,{'content-type': 'text/plain; charset: utf-8'}
@app.route('/api/<resource>/<primaryKeyValues>', methods = ["GET", "PUT", "DELETE"])
def get_specific_resource(resource,primaryKeyValues):
    primaryKeyValues=primaryKeyValues.split("_")
    fields,q = parseArgs()
    primaryColumns = getPrimaryKeyColumns(resource)
    if request.method == "GET":
        limit,offset=getLimitOffset(q)
        templateToFind = dict(zip(primaryColumns, primaryKeyValues))
        if len(primaryColumns) != len(primaryKeyValues):
            print("Cannot Query: Expecting "+ str(len(primaryColumns)) + " primary key elements, received " + str(len(primaryKeyValues))+".")
            return "Cannot Query: Expecting "+ str(len(primaryColumns)) + " primary key elements, received " + str(len(primaryKeyValues))+".", 404, {'Content-Type': 'application/json; charset=utf-8'}
        if not fields:
            results,links = find_by_template(resource,templateToFind)    
        else:
            try:
                results,links = find_by_template(resource,templateToFind,fields)
            except Exception:
                print("Could Not Find Fields Listed")
                return "Could Not Find Fields Listed" + json.dumps(templateToFind), 404, {'Content-Type': 'application/json; charset=utf-8'}
        if results:
            print(json.dumps(results, indent=2))
            if links:
                print(json.dumps(links, indent=2))
                return json.dumps(results, indent=2)+json.dumps(links, indent=2), 200, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return json.dumps(results, indent=2), 200, {'Content-Type': 'application/json; charset=utf-8'}
        else:
            print("Could Not Find Entry with these elements" + json.dumps(fields))
            return "Could Not Find Entry with these elements" + json.dumps(fields), 404, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == "PUT":
        if len(primaryColumns) != len(primaryKeyValues):
            print("Cannot Update: Expecting "+ str(len(primaryColumns)) + " primary key elements, received " + str(len(primaryKeyValues))+".")
            return "Cannot Update: Expecting "+ str(len(primaryColumns)) + " primary key elements, received " + str(len(primaryKeyValues))+".", 404, {'Content-Type': 'application/json; charset=utf-8'}
        templateToUpdate = dict(zip(primaryColumns, primaryKeyValues))
        r,l= find_by_template(resource,templateToUpdate)
        if not r:
            print("Cannot update table: Couldn't find row specified by: "+ json.dumps(templateToUpdate)+ " in table "+resource)
            return "Cannot update table: Couldn't find row specified by: "+ json.dumps(templateToUpdate)+ " in table "+resource, 404, {'Content-Type': 'application/json; charset=utf-8'}
        body=getBody()
        print(body)
        error = update(resource,body,templateToUpdate)
        splitError = str(error).split(',')
        if splitError[0] == "(1364":
            print("Cannot update table, missing some primary keys ")
            return "Cannot update table, missing some primary keys ", 404, {'Content-Type': 'application/json; charset=utf-8'}
        elif splitError[0] == "(1054":
            print("Cannot update table, body contains rows not in table: "+str(error))
            return "Cannot update table, body contains rows not in table: "+str(error), 404, {'Content-Type': 'application/json; charset=utf-8'}
        elif error is None:
            print("Updated")
            return "Updated", 200, {'Content-Type': 'application/json; charset=utf-8'}
        else:
            print("Cannot update table, found error: "+ str(error))
            return "Cannot update table, found error: "+ str(error), 404, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == "DELETE":
        if len(primaryColumns) != len(primaryKeyValues):
            print("Cannot Delete: Expecting "+ str(len(primaryColumns)) + " primary key elements, received " + str(len(primaryKeyValues))+".")
            return "Cannot Delete: Expecting "+ str(len(primaryColumns)) + " primary key elements, received " + str(len(primaryKeyValues))+".", 404, {'Content-Type': 'application/json; charset=utf-8'}
        templateToDelete = dict(zip(primaryColumns, primaryKeyValues))
        r,l= find_by_template(resource,templateToDelete)
        if not r:
            print("Cannot delete: Couldn't find row specified by: "+ json.dumps(templateToDelete)+ " in table "+resource)
            return "Cannot delete: Couldn't find row specified by: "+ json.dumps(templateToDelete)+ " in table "+resource, 404, {'Content-Type': 'application/json; charset=utf-8'}
        error = delete(resource,templateToDelete)
        splitError = str(error).split(',')
        if splitError[0] == "(1364":
            print("Cannot delete, missing some primary keys ")
            return "Cannot delete, missing some primary keys ", 404, {'Content-Type': 'application/json; charset=utf-8'}
        elif error is None:
            print("Deleted")
            return "Deleted", 200, {'Content-Type': 'application/json; charset=utf-8'}
        else:
            print("Cannot delete, found error: "+ str(error))
            return "Cannot delete, found error: "+ str(error), 404, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        return "Method " + request.method + " on resource " + resource +"/"+ primaryKeyValues+ \
               " not implemented",501,{'content-type': 'text/plain; charset: utf-8'}
@app.route('/api/<resource>', methods = ["GET", "POST"])
def get_resource(resource):
    fields,query = parseArgs()
    if request.method == "GET":
        limit,offset=getLimitOffset(query)
        if not fields:
            results,links = find_by_template(resource,query,lim=limit,offs=offset)
        else:        
            results,links = find_by_template(resource,query,fields,lim=limit,offs=offset)
    
        if results:
            print(json.dumps(results, indent=2))
            if links:
                print(json.dumps(links, indent=2))
                return json.dumps(results, indent=2)+json.dumps(links, indent=2), 200, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return json.dumps(results, indent=2), 200, {'Content-Type': 'application/json; charset=utf-8'}
        else:
            print("Could Not Find")
            return "NOT FOUND", 404
    elif request.method == "POST":
        body=getBody()
        error = insert(resource,body)
        splitError = str(error).split(',')
        if splitError[0] == "(1364":
            print("Cannot insert into table, missing some primary keys ")
            return "Cannot insert into table, missing some primary keys ", 404, {'Content-Type': 'application/json; charset=utf-8'}
        elif splitError[0] == "(1054":
            print("Cannot insert into table, body contains rows not in table: "+str(error))
            return "Cannot insert into table, body contains rows not in table: "+str(error), 404, {'Content-Type': 'application/json; charset=utf-8'}
        elif error is None:
            return "Inserted", 200, {'Content-Type': 'application/json; charset=utf-8'}
        else:
            print("Cannot insert into table, found error: "+ str(error))
            return "Cannot insert into table, found error: "+ str(error), 404, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        print("Method " + request.method + " on resource " + resource + \
               " not implemented")
        return "Method " + request.method + " on resource " + resource + \
               " not implemented",501,{'content-type': 'text/plain; charset: utf-8'}    
               
@app.route('/api/teammates/<playerId>', methods = ["GET"])
def get_teammates(playerId):
    fields,query = parseArgs()
    lim,offs=getLimitOffset(query)
    cnx = pymysql.connect(host='localhost',
                          user='dbuser',
                          password='dbuser',
                          db='baseball',
                          charset='utf8mb4',
                          cursorclass=pymysql.cursors.DictCursor,
                          autocommit=True)
    cursor = cnx.cursor()
    q="select SQL_CALC_FOUND_ROWS a.playerid, b.playerid as teammateid, b.yearid from \
    (select playerid, yearid, teamid from appearances where \
     (playerID = '"+ playerId +"') )  as a \
JOIN \
	(select playerid, yearid, teamid from appearances) as b \
on a.yearid = b.yearid and a.teamid = b.teamid \
 LIMIT "+lim+" OFFSET "+offs+";"
    try:
        cursor.execute(q)
        results=cursor.fetchall()
    except Exception as e:
        print("Found exception: "+ str(e))
        return "Found exception: "+ str(e), 404, {'Content-Type': 'application/json; charset=utf-8'}
    if not results:
        print("Cannot find playerID: "+ playerId)
        return "Cannot find playerID: "+ playerId, 404, {'Content-Type': 'application/json; charset=utf-8'}
    
    q = "Select FOUND_ROWS();"
    try:
        cursor.execute(q)
        totalLength=cursor.fetchall()
    except Exception as e:
        return [],{}
    links={}
    totalLength = int(totalLength[0]["FOUND_ROWS()"])
    base=request.base_url
    query=dict(copy.copy(request.args))
    urlString=base
    otherQueries=False
    for k,v in query.items():
        if k.lower() != "offset" and k.lower() != "limit" :
            otherQueries=True
            if urlString == base:
                urlString=urlString+"?"+ k+"="+', '.join(v)
            else:
                urlString=urlString+"&"+ k+"="+', '.join(v)
    if otherQueries:
        links["current:"] = urlString + "&offset="+offs+"&limit="+lim
        if totalLength>int(offs)+int(lim):
            newOffs=str(int(offs)+int(lim))
            links["next:"] = urlString + "&offset="+newOffs+"&limit="+lim
        newOffs=str(int(offs)-int(lim))
        if int(newOffs)>=0:
            links["previous:"] = urlString + "&offset="+newOffs+"&limit="+lim
    else:
        links["current:"] = urlString + "?&offset="+offs+"&limit="+lim
        if totalLength>int(offs)+int(lim):
            newOffs=str(int(offs)+int(lim))
            links["next:"] = urlString + "?&offset="+newOffs+"&limit="+lim
        newOffs=str(int(offs)-int(lim))
        if int(newOffs)>=0:
            links["previous:"] = urlString + "?&offset="+newOffs+"&limit="+lim
    
    
    teammateDict={}
    for entry in results:
        if entry["teammateid"] not in teammateDict:
            teammateDict[entry["teammateid"]]=[int(entry["yearid"])]
        else:
            teammateDict[entry["teammateid"]].append(int(entry["yearid"]))
    finalTeammates=[]
    for k,v in teammateDict.items():
        teammateEntry={}
        teammateEntry["ID"]=playerId
        teammateEntry["teammateid"]=k
        teammateEntry["first year"]=min(v)
        teammateEntry["last year"]=max(v)
        teammateEntry["count"]=len(v)
        finalTeammates.append(teammateEntry)
    print(json.dumps(finalTeammates, indent=2))
    print(json.dumps(links, indent=2))
    return json.dumps(finalTeammates, indent=2)+json.dumps(links, indent=2), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/api/people/<playerId>/career_stats', methods = ["GET"])
def get_stats(playerId):
    fields,query = parseArgs()
    lim,offs=getLimitOffset(query)
    cnx = pymysql.connect(host='localhost',
                          user='dbuser',
                          password='dbuser',
                          db='baseball',
                          charset='utf8mb4',
                          cursorclass=pymysql.cursors.DictCursor,
                          autocommit=True)
    cursor = cnx.cursor()    
    q="select SQL_CALC_FOUND_ROWS a.playerID, a.teamid, a.yearID, a.g_all, b.H, b.AB, c.a, c.e from \
    (select playerID, teamID, yearID, g_all from appearances where \
     (playerID = '"+ playerId +"') )  as a \
JOIN \
	(select H, AB, yearid from batting where \
     (playerID = '"+ playerId +"') )  as b \
on a.yearid = b.yearid \
JOIN \
	(select A, E, yearid from fielding where \
     (playerID = '"+ playerId +"') )  as c \
on b.yearid = c.yearid\
 LIMIT "+lim+" OFFSET "+offs+";"
 
    try:
        cursor.execute(q)
        results=cursor.fetchall()
    except Exception as e:
        print("Found exception: "+ str(e))
        return "Found exception: "+ str(e), 404, {'Content-Type': 'application/json; charset=utf-8'}
    if not results:
        print("Cannot find playerID: "+ playerId)
        return "Cannot find playerID: "+ playerId, 404, {'Content-Type': 'application/json; charset=utf-8'}
    
    q = "Select FOUND_ROWS();"
    try:
        cursor.execute(q)
        totalLength=cursor.fetchall()
    except Exception as e:
        return [],{}
    links={}
    totalLength = int(totalLength[0]["FOUND_ROWS()"])
    base=request.base_url
    query=dict(copy.copy(request.args))
    urlString=base
    otherQueries=False
    for k,v in query.items():
        if k.lower() != "offset" and k.lower() != "limit" :
            otherQueries=True
            if urlString == base:
                urlString=urlString+"?"+ k+"="+', '.join(v)
            else:
                urlString=urlString+"&"+ k+"="+', '.join(v)
    if otherQueries:
        links["current:"] = urlString + "&offset="+offs+"&limit="+lim
        if totalLength>int(offs)+int(lim):
            newOffs=str(int(offs)+int(lim))
            links["next:"] = urlString + "&offset="+newOffs+"&limit="+lim
        newOffs=str(int(offs)-int(lim))
        if int(newOffs)>=0:
            links["previous:"] = urlString + "&offset="+newOffs+"&limit="+lim
    else:
        links["current:"] = urlString + "?&offset="+offs+"&limit="+lim
        if totalLength>int(offs)+int(lim):
            newOffs=str(int(offs)+int(lim))
            links["next:"] = urlString + "?&offset="+newOffs+"&limit="+lim
        newOffs=str(int(offs)-int(lim))
        if int(newOffs)>=0:
            links["previous:"] = urlString + "?&offset="+newOffs+"&limit="+lim
    print(json.dumps(results, indent=2))
    print(json.dumps(links, indent=2))
    return json.dumps(results, indent=2)+json.dumps(links, indent=2), 200, {'Content-Type': 'application/json; charset=utf-8'}
    
    
@app.route('/api/roster', methods = ["GET"])
#@cross_origin()
def get_roster():
    fields,query = parseArgs()
    lim,offs=getLimitOffset(query)
    cnx = pymysql.connect(host='localhost',
                          user='dbuser',
                          password='dbuser',
                          db='baseball',
                          charset='utf8mb4',
                          cursorclass=pymysql.cursors.DictCursor,
                          autocommit=True)
    f,query = parseArgs()
    query = dict((k.lower(), v) for k,v in query.items())
    teamid=query["teamid"]
    yearid=query["yearid"]  
    cursor = cnx.cursor()    
    q="select SQL_CALC_FOUND_ROWS d.namefirst, d.namelast, a.playerID, a.teamid, a.yearID, a.g_all, b.H, b.AB, c.a, c.e from \
    (select playerID, teamID, yearID, g_all from appearances where \
     (teamID = '"+ teamid +"' and yearID = '"+ yearid +"') )  as a \
JOIN \
	(select playerid, H, AB, yearid from batting where \
     (teamID = '"+ teamid +"' and yearID = '"+ yearid +"') )  as b \
on a.playerid = b.playerid \
JOIN \
	(select playerid, A, E, yearid from fielding where \
     (teamID = '"+ teamid +"' and yearID = '"+ yearid +"') )  as c \
on b.playerid = c.playerid \
JOIN \
	(select playerid, namefirst, namelast from people) \
    as d \
on c.playerid = d.playerid \
 LIMIT "+lim+" OFFSET "+offs+";"

    try:  
        cursor.execute(q)
        results=cursor.fetchall()
    except Exception as e:
        print("Found exception: "+ str(e))
        return "Found exception: "+ str(e), 404, {'Content-Type': 'application/json; charset=utf-8'}
    if not results:
        print("Cannot find Team or Year: "+teamid+' '+yearid)
        return "Cannot find Team or Year: "+teamid+' '+yearid, 404, {'Content-Type': 'application/json; charset=utf-8'}

    q = "Select FOUND_ROWS();"
    try:
        cursor.execute(q)
        totalLength=cursor.fetchall()
    except Exception as e:
        return [],{}
    links={}
    totalLength = int(totalLength[0]["FOUND_ROWS()"])
    base=request.base_url
    query=dict(copy.copy(request.args))
    urlString=base
    otherQueries=False
    for k,v in query.items():
        if k.lower() != "offset" and k.lower() != "limit" :
            otherQueries=True
            if urlString == base:
                urlString=urlString+"?"+ k+"="+v
            else:
                urlString=urlString+"&"+ k+"="+v
    if otherQueries:
        links["current:"] = urlString + "&offset="+offs+"&limit="+lim
        if totalLength>int(offs)+int(lim):
            newOffs=str(int(offs)+int(lim))
            links["next:"] = urlString + "&offset="+newOffs+"&limit="+lim
        newOffs=str(int(offs)-int(lim))
        if int(newOffs)>=0:
            links["previous:"] = urlString + "&offset="+newOffs+"&limit="+lim
    else:
        links["current:"] = urlString + "?&offset="+offs+"&limit="+lim
        if totalLength>int(offs)+int(lim):
            newOffs=str(int(offs)+int(lim))
            links["next:"] = urlString + "?&offset="+newOffs+"&limit="+lim
        newOffs=str(int(offs)-int(lim))
        if int(newOffs)>=0:
            links["previous:"] = urlString + "?&offset="+newOffs+"&limit="+lim
    print(json.dumps(results, indent=2))
    print(json.dumps(links, indent=2))
    return json.dumps(results, indent=2)+json.dumps(links, indent=2), 200, {'Content-Type': 'application/json; charset=utf-8','Access-Control-Allow-Origin':'*'}
    
if __name__ == '__main__':
    app.run()