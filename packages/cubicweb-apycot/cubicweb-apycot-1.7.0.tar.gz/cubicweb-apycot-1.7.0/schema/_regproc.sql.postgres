/* -*- sql -*- 

   postgres specific registered procedures, 
   require the plpythonu language installed 

*/

CREATE FUNCTION severity_sort_value(text) RETURNS int
    AS 'return {"DEBUG": 0, "INFO": 10, "WARNING": 20, "ERROR": 30, "FATAL": 40}[args[0]]'
    LANGUAGE plpythonu;
