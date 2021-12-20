def optimize(inputFile,outputFile):
    '''This function will take an excel sheet in the same format as 'data.xlsx' as an input and requires a desired
    file path for the output file. It will return what is the minimum transportation cost achievable with the 
    input data. It will also return the 5 fulfillment centers with the most negative shadow prices. These 5 fulfillment
    centers are the recommended FCs to make small scale capacity increases at in order to lower the minimum 
    transportation cost. ''' 
    import pandas as pd
    from gurobipy import Model, GRB
    fcs = pd.read_excel(inputFile,index_col=0) 
    regions = pd.read_excel(inputFile,sheet_name = 'Regions',index_col=0) 
    distance = pd.read_excel(inputFile,sheet_name = 'Distances',index_col=0)
    items = pd.read_excel(inputFile,sheet_name = 'Items',index_col=0) 
    demand = pd.read_excel(inputFile,sheet_name = 'Demand',index_col=0) 
    I = fcs.index                
    J = regions.index            
    K = items.index              
    w = items['shipping_weight']              
    q = fcs['capacity']          
    s = items['storage_size']    
    mod = Model()
    x = mod.addVars(I,J,K)
    mod.setObjective(sum(1.38*w[k]*distance.loc[j,i]*x[i,j,k] for i in I for j in J for k in K))
    fc_constraint = {}
    for i in I:
        fc_constraint[i]=mod.addConstr(sum(x[i,j,k]*s[k] for j in J for k in K)<=q[i])
    for k in K:
        for j in J:
            mod.addConstr(sum(x[i,j,k] for i in I)>=demand.loc[k,j])
    mod.setParam('outputflag',False)
    mod.optimize()
    writer=pd.ExcelWriter(outputFile)
    pd.DataFrame([mod.objVal],columns=['Objective Value']).to_excel(writer,sheet_name='Summary',index=False)
    df = pd.DataFrame(columns=['FC_name','region_ID','item_ID','shipment'])
    for i in I:
        for j in J:
            for k in K:
                if x[i,j,k].x > 0:
                    newrow = {'FC_name':i,'region_ID':j,'item_ID':k,'shipment':x[i,j,k].x}
                    df = df.append(newrow,True)
    df.to_excel(writer,sheet_name='Solution',index=False)
    shadow_prices = pd.DataFrame(columns=['FC_name', 'shadow_price'])
    for key, value in fc_constraint.items():
            shadow_prices = shadow_prices.append({'FC_name': key, 'shadow_price': value.pi}, True)
    shadow_prices = shadow_prices.sort_values(by = 'shadow_price').reset_index(drop = True).loc[:4, :]
    shadow_prices.to_excel(writer, sheet_name='Capacity Constraints', index=False)
    writer.save() 
if __name__=='__main__':
    import sys, os
    if len(sys.argv)!=3:
        print('Correct syntax: python lab2_code.py inputFile outputFile')
    else:
        inputFile=sys.argv[1]
        outputFile=sys.argv[2]
        if os.path.exists(inputFile):
            optimize(inputFile,outputFile)
            print(f'Successfully optimized. Results in "{outputFile}"')
        else:
            print(f'File "{inputFile}" not found!')  