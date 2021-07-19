import sqlite3 as sl

###________________COMMAND GENERATOR FOR SQLITE3
##
##def gen_cmd(data, table_name, gen_n, ind_n):
##
##    fmt = 'GEN IND'
##    val = '%d %d'%(gen_n, ind_n)
##
##    for c,v in enumerate(data):
##
##        fmt+=' P%d'%(c+1)
##        val+=str(' %f'%(v))
##
##    fmt = fmt.strip().replace(' ',',')
##    val = val.strip().replace(' ',',')
##
##    cmd = "INSERT INTO %s ("%(table_name)+fmt+") VALUES ("+val+")"
##
##    return cmd
##
###________________WRITE POPULATION IN DB
##
##def model_writter(data, table_name, gen_n, ind_n, flag):
##
##    dbase_file = 'model.db'
##
##    con = sl.connect(dbase_file)
##
##    with con:
##
##        cur = con.cursor()
##
##        if flag:
##
##            try:
##
##                cur.execute("DROP TABLE IF EXISTS %s"%(table_name))
##                cur.execute("CREATE TABLE %s (GEN INTEGER)"%(table_name))
##                cur.execute("ALTER TABLE %s ADD COLUMN IND INTEGER"%(table_name)) 
##
##
##                for col in range(len(data)):
##
##                    cur.execute("ALTER TABLE %s ADD COLUMN P%d REAL"%(table_name, col+1))
##
##                cur.execute(gen_cmd(data, table_name, gen_n, ind_n))
##
##            except sl.OperationalError:
##
##                pass 
##        else:
##
##            cur.execute(gen_cmd(data, table_name, gen_n, ind_n))
##        
####Example
####model_writter([121,22,2], 'noisy_tor_1', 1, 2, True)
