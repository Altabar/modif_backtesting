
from operator import index
from pickle import FALSE
import pandas as pd
import math
from datetime import datetime
import matplotlib.pyplot as plt
# from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
# from plotly.offline import iplot, init_notebook_mode
# Using plotly + cufflinks in offline mode
# import cufflinks
# cufflinks.go_offline(connected=True)
# init_notebook_mode(connected=True)
# from tkinter import font
# import random
import numpy as np
import seaborn as sns
import datetime

class Backtesting():

    def simple_spot_backtest_analys(self, dfTrades, dfTest, pairSymbol, timeframe):
        # -- BackTest Analyses --
        dfTrades = dfTrades.set_index(dfTrades['date'])
        dfTrades.index = pd.to_datetime(dfTrades.index)
        dfTrades['resultat'] = dfTrades['wallet'].diff()
        dfTrades['resultat%'] = dfTrades['wallet'].pct_change()*100
        dfTrades.loc[dfTrades['position'] == 'Buy', 'resultat'] = None
        dfTrades.loc[dfTrades['position'] == 'Buy', 'resultat%'] = None

        dfTrades['tradeIs'] = ''
        dfTrades.loc[dfTrades['resultat'] > 0, 'tradeIs'] = 'Good'
        dfTrades.loc[dfTrades['resultat'] <= 0, 'tradeIs'] = 'Bad'

        dfTrades['walletAth'] = dfTrades['wallet'].cummax()
        dfTrades['drawDown'] = dfTrades['walletAth'] - dfTrades['wallet']
        dfTrades['drawDownPct'] = dfTrades['drawDown'] / dfTrades['walletAth']

        wallet = dfTrades.iloc[-1]['wallet']
        iniClose = dfTest.iloc[0]['close']
        lastClose = dfTest.iloc[len(dfTest)-1]['close']
        holdPercentage = ((lastClose - iniClose)/iniClose) * 100
        initalWallet = dfTrades.iloc[0]['wallet']
        algoPercentage = ((wallet - initalWallet)/initalWallet) * 100
        holdFinalWallet = initalWallet + initalWallet*(holdPercentage/100)
        vsHoldPercentage = ((wallet/holdFinalWallet)-1)*100

        try:
            tradesPerformance = round(dfTrades.loc[(dfTrades['tradeIs'] == 'Good') | (dfTrades['tradeIs'] == 'Bad'), 'resultat%'].sum()
                                      / dfTrades.loc[(dfTrades['tradeIs'] == 'Good') | (dfTrades['tradeIs'] == 'Bad'), 'resultat%'].count(), 2)
        except:
            tradesPerformance = 0
            print(
                "/!\ There is no Good or Bad Trades in your BackTest, maybe a problem...")

        try:
            totalGoodTrades = len(dfTrades.loc[dfTrades['tradeIs'] == 'Good'])
            AveragePercentagePositivTrades = round(dfTrades.loc[dfTrades['tradeIs'] == 'Good', 'resultat%'].sum()
                                                    / totalGoodTrades, 2)
            idbest = dfTrades.loc[dfTrades['tradeIs']
                                    == 'Good', 'resultat%'].idxmax()
            bestTrade = str(
                round(dfTrades.loc[dfTrades['tradeIs'] == 'Good', 'resultat%'].max(), 2))
        except:
            totalGoodTrades = 0
            AveragePercentagePositivTrades = 0
            idbest = ''
            bestTrade = 0
            print("/!\ There is no Good Trades in your BackTest, maybe a problem...")

        try:
            totalBadTrades = len(dfTrades.loc[dfTrades['tradeIs'] == 'Bad'])
            AveragePercentageNegativTrades = round(dfTrades.loc[dfTrades['tradeIs'] == 'Bad', 'resultat%'].sum()
                                                    / totalBadTrades, 2)
            idworst = dfTrades.loc[dfTrades['tradeIs']
                                    == 'Bad', 'resultat%'].idxmin()
            worstTrade = round(
                dfTrades.loc[dfTrades['tradeIs'] == 'Bad', 'resultat%'].min(), 2)
        except:
            totalBadTrades = 0
            AveragePercentageNegativTrades = 0
            idworst = ''
            worstTrade = 0
            print("/!\ There is no Bad Trades in your BackTest, maybe a problem...")

        totalTrades = totalBadTrades + totalGoodTrades
        winRateRatio = (totalGoodTrades/totalTrades) * 100

        try:
            dfTrades['timeDeltaTrade'] = dfTrades["timeSince"]
            dfTrades['timeDeltaNoTrade'] = dfTrades['timeDeltaTrade']
            dfTrades.loc[dfTrades['position'] ==
                         'Buy', 'timeDeltaTrade'] = None
            dfTrades.loc[dfTrades['position'] ==
                         'Sell', 'timeDeltaNoTrade'] = None
        except:
            print("/!\ Error in time delta")
            dfTrades['timeDeltaTrade'] = 0
            dfTrades['timeDeltaNoTrade'] = 0

        reasons = dfTrades['reason'].unique()

        print("Pair Symbol :", pairSymbol, '| Timeframe :', timeframe)
        print("Period : [" + str(dfTest.index[0]) + "] -> [" +
              str(dfTest.index[len(dfTest)-1]) + "]")
        print("Starting balance :", initalWallet, "$")

        print("\n----- General Informations -----")
        print("Final balance :", round(wallet, 2), "$")
        print("Performance vs US Dollar :", round(algoPercentage, 2), "%")
        print("Buy and Hold Performance :", round(holdPercentage, 2), "%")
        print("Performance vs Buy and Hold :", round(vsHoldPercentage, 2), "%")
        print("Best trade : +"+bestTrade, "%, the", idbest)
        print("Worst trade :", worstTrade, "%, the", idworst)
        print("Worst drawDown : -", str(
            round(100*dfTrades['drawDownPct'].max(), 2)), "%")
        print("Total fees : ", round(dfTrades['frais'].sum(), 2), "$")

        print("\n----- Trades Informations -----")
        print("Total trades on period :", totalTrades)
        print("Number of positive trades :", totalGoodTrades)
        print("Number of negative trades : ", totalBadTrades)
        print("Trades win rate ratio :", round(winRateRatio, 2), '%')
        print("Average trades performance :", tradesPerformance, "%")
        print("Average positive trades :", AveragePercentagePositivTrades, "%")
        print("Average negative trades :", AveragePercentageNegativTrades, "%")

        print("\n----- Time Informations -----")
        print("Average time duration for a trade :", round(
            dfTrades['timeDeltaTrade'].mean(skipna=True), 2), "periods")
        print("Maximum time duration for a trade :",
              dfTrades['timeDeltaTrade'].max(skipna=True), "periods")
        print("Minimum time duration for a trade :",
              dfTrades['timeDeltaTrade'].min(skipna=True), "periods")
        print("Average time duration between two trades :", round(
            dfTrades['timeDeltaNoTrade'].mean(skipna=True), 2), "periods")
        print("Maximum time duration between two trades :",
              dfTrades['timeDeltaNoTrade'].max(skipna=True), "periods")
        print("Minimum time duration between two trades :",
              dfTrades['timeDeltaNoTrade'].min(skipna=True), "periods")

        print("\n----- Trades Reasons -----")
        reasons = dfTrades['reason'].unique()
        for r in reasons:
            print(r+" number :", dfTrades.groupby('reason')
                  ['date'].nunique()[r])

        return dfTrades

    def multi_spot_backtest_analys(self, dfTrades, dfTest, pairList, timeframe):
        # -- BackTest Analyses --
        dfTrades = dfTrades.set_index(dfTrades['date'])
        dfTrades.index = pd.to_datetime(dfTrades.index)
        dfTrades['resultat'] = dfTrades['wallet'].diff()
        dfTrades['resultat%'] = dfTrades['wallet'].pct_change()*100
        dfTrades.loc[dfTrades['position'] == 'Buy', 'resultat'] = None
        dfTrades.loc[dfTrades['position'] == 'Buy', 'resultat%'] = None

        dfTrades['tradeIs'] = ''
        dfTrades.loc[dfTrades['resultat'] > 0, 'tradeIs'] = 'Good'
        dfTrades.loc[dfTrades['resultat'] <= 0, 'tradeIs'] = 'Bad'

        dfTrades['walletAth'] = dfTrades['wallet'].cummax()
        dfTrades['drawDown'] = dfTrades['walletAth'] - dfTrades['wallet']
        dfTrades['drawDownPct'] = dfTrades['drawDown'] / dfTrades['walletAth']

        wallet = dfTrades.iloc[-1]['wallet']
        iniClose = dfTest.iloc[0]['close']
        lastClose = dfTest.iloc[len(dfTest)-1]['close']
        holdPercentage = ((lastClose - iniClose)/iniClose) * 100
        initalWallet = dfTrades.iloc[0]['wallet']
        algoPercentage = ((wallet - initalWallet)/initalWallet) * 100
        holdFinalWallet = initalWallet + initalWallet*(holdPercentage/100)
        vsHoldPercentage = ((wallet/holdFinalWallet)-1)*100

        try:
            tradesPerformance = round(dfTrades.loc[(dfTrades['tradeIs'] == 'Good') | (dfTrades['tradeIs'] == 'Bad'), 'resultat%'].sum()
                                        / dfTrades.loc[(dfTrades['tradeIs'] == 'Good') | (dfTrades['tradeIs'] == 'Bad'), 'resultat%'].count(), 2)
        except:
            tradesPerformance = 0
            print(
                "/!\ There is no Good or Bad Trades in your BackTest, maybe a problem...")

        try:
            totalGoodTrades = len(dfTrades.loc[dfTrades['tradeIs'] == 'Good'])
            AveragePercentagePositivTrades = round(dfTrades.loc[dfTrades['tradeIs'] == 'Good', 'resultat%'].sum()
                                                    / totalGoodTrades, 2)
            idbest = dfTrades.loc[dfTrades['tradeIs']
                                    == 'Good', 'resultat%'].idxmax()
            bestTrade = str(
                round(dfTrades.loc[dfTrades['tradeIs'] == 'Good', 'resultat%'].max(), 2))
        except:
            totalGoodTrades = 0
            AveragePercentagePositivTrades = 0
            idbest = ''
            bestTrade = 0
            print("/!\ There is no Good Trades in your BackTest, maybe a problem...")

        try:
            totalBadTrades = len(dfTrades.loc[dfTrades['tradeIs'] == 'Bad'])
            AveragePercentageNegativTrades = round(dfTrades.loc[dfTrades['tradeIs'] == 'Bad', 'resultat%'].sum()
                                                    / totalBadTrades, 2)
            idworst = dfTrades.loc[dfTrades['tradeIs']
                                    == 'Bad', 'resultat%'].idxmin()
            worstTrade = round(
                dfTrades.loc[dfTrades['tradeIs'] == 'Bad', 'resultat%'].min(), 2)
        except:
            totalBadTrades = 0
            AveragePercentageNegativTrades = 0
            idworst = ''
            worstTrade = 0
            print("/!\ There is no Bad Trades in your BackTest, maybe a problem...")

        totalTrades = totalBadTrades + totalGoodTrades
        winRateRatio = (totalGoodTrades/totalTrades) * 100


        print("Trading Bot on :", len(pairList), 'coins | Timeframe :', timeframe)
        print("Period : [" + str(dfTest.index[0]) + "] -> [" +
                str(dfTest.index[len(dfTest)-1]) + "]")
        print("Starting balance :", initalWallet, "$")

        print("\n----- General Informations -----")
        print("Final balance :", round(wallet, 2), "$")
        print("Performance vs US Dollar :", round(algoPercentage, 2), "%")
        print("Bitcoin Buy and Hold Performence :", round(holdPercentage, 2), "%")
        print("Performance vs Buy and Hold :", round(vsHoldPercentage, 2), "%")
        print("Best trade : +"+bestTrade, "%, the", idbest)
        print("Worst trade :", worstTrade, "%, the", idworst)
        print("Worst drawDown : -", str(
            round(100*dfTrades['drawDownPct'].max(), 2)), "%")
        print("Total fees : ", round(dfTrades['frais'].sum(), 2), "$")

        print("\n----- Trades Informations -----")
        print("Total trades on period :", totalTrades)
        print("Number of positive trades :", totalGoodTrades)
        print("Number of negative trades : ", totalBadTrades)
        print("Trades win rate ratio :", round(winRateRatio, 2), '%')
        print("Average trades performance :", tradesPerformance, "%")
        print("Average positive trades :", AveragePercentagePositivTrades, "%")
        print("Average negative trades :", AveragePercentageNegativTrades, "%")

        print("\n----- Trades Reasons -----")
        print(dfTrades['reason'].value_counts())

        print("\n----- Pair Result -----")
        dash = '-' * 95
        print(dash)
        print('{:<6s}{:>10s}{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}'.format(
            "Trades","Pair","Sum-result","Mean-trade","Worst-trade","Best-trade","Win-rate"
            ))
        print(dash)
        for pair in pairList:
            try:
                dfPairLoc = dfTrades.loc[dfTrades['symbol'] == pair, 'resultat%']
                pairGoodTrade = len(dfTrades.loc[(dfTrades['symbol'] == pair) & (dfTrades['resultat%'] > 0)])
                pairTotalTrade = int(len(dfPairLoc)/2)
                pairResult = str(round(dfPairLoc.sum(),2))+' %'
                pairAverage = str(round(dfPairLoc.mean(),2))+' %'
                pairMin = str(round(dfPairLoc.min(),2))+' %'
                pairMax = str(round(dfPairLoc.max(),2))+' %'
                pairWinRate = str(round(100*(pairGoodTrade/pairTotalTrade),2))+' %'
                print('{:<6d}{:>10s}{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}'.format(
                    pairTotalTrade,pair,pairResult,pairAverage,pairMin,pairMax,pairWinRate
                ))
            except:
                pass

        return dfTrades

    def get_result_by_month(self, dfTrades):
        lastMonth = int(dfTrades.iloc[-1]['date'].month)
        lastYear = int(dfTrades.iloc[-1]['date'].year)
        dfTrades = dfTrades.set_index(dfTrades['date'])
        dfTrades.index = pd.to_datetime(dfTrades.index)
        myMonth = int(dfTrades.iloc[0]['date'].month)
        myYear = int(dfTrades.iloc[0]['date'].year)
        while myYear != lastYear or myMonth != lastMonth:
            myString = str(myYear) + "-" + str(myMonth)
            try:
                myResult = (dfTrades.loc[myString].iloc[-1]['wallet'] -
                            dfTrades.loc[myString].iloc[0]['wallet'])/dfTrades.loc[myString].iloc[0]['wallet']
            except:
                myResult = 0
            print(myYear, myMonth, round(myResult*100, 2), "%")
            if myMonth < 12:
                myMonth += 1
            else:
                myMonth = 1
                myYear += 1

        myString = str(lastYear) + "-" + str(lastMonth)
        try:
            myResult = (dfTrades.loc[myString].iloc[-1]['wallet'] -
                        dfTrades.loc[myString].iloc[0]['wallet'])/dfTrades.loc[myString].iloc[0]['wallet']
        except:
            myResult = 0
        print(lastYear, lastMonth, round(myResult*100, 2), "%")

    def plot_wallet_vs_price(self, dfTrades):
        dfTrades = dfTrades.set_index(dfTrades['date'])
        dfTrades.index = pd.to_datetime(dfTrades.index)
        dfTrades[['wallet','price']].plot(subplots=True, figsize=(20, 5))
        print("\n----- Plot -----")

    
    def plot_wallet_evolution(self, dfTrades):
        dfPlotly = dfTrades.copy()
        dfPlotly = dfPlotly.set_index(dfPlotly['date'])
        dfPlotly.index = pd.to_datetime(dfPlotly.index)
        dfPlotly.drop(dfPlotly.columns.difference(['wallet','price','reason','SL','index_achat','index_vente']), axis=1, inplace=True)
        
        # fig = go.Figure()
        
        stocks = ['wallet', 'price']
        # print(dfPlotly[stocks].tail())
        
        traces = {}
        for i in range(0, len(stocks)):
            
            traces['trace_' + str(i)]=go.Scatter(
                # mode='lines+markers',
                mode='lines+text',
                # mode='lines',
                x=dfPlotly.index,
                y=dfPlotly[stocks[i]].values,
                name=stocks[i],
            )
        data=list(traces.values())
        # fig.update_traces()  
        fig=go.Figure(data)               
                   
        # shapes update        
        ply_shapes = {}
        for i in range(0, len(dfPlotly)):
            
            if dfPlotly['reason'].iloc[i] == "Sell Stop Loss":
                if dfPlotly['wallet'].iloc[i] < dfPlotly['wallet'].iloc[i-1]:
                    colors = "red"
                    epaisseur = 1
                    
                elif dfPlotly['wallet'].iloc[i] >= dfPlotly['wallet'].iloc[i-1]:
                    colors = "black"
                    epaisseur = 1
                                           
            elif dfPlotly['reason'].iloc[i] == "Sell Cond. Order":
                if dfPlotly['wallet'].iloc[i] >= dfPlotly['wallet'].iloc[i-1]:
                    colors = "slategray"
                    epaisseur = 1
                elif dfPlotly['wallet'].iloc[i] < dfPlotly['wallet'].iloc[i-1]:
                    colors = "fuchsia"
                    epaisseur = 1               
                
            elif dfPlotly['reason'].iloc[i] == "Sell Take Profit":
                colors = "gold"
                epaisseur = 2
               
            elif dfPlotly['reason'].iloc[i] == "Buy Market Order":
                colors = "green"
                epaisseur = 1
                
            ply_shapes['shape_' + str(i)]=go.layout.Shape(type="line",
                                                            x0=dfPlotly.index[i],
                                                            y0=dfPlotly['wallet'].iloc[i],
                                                            x1=dfPlotly.index[i],
                                                            y1=dfPlotly['price'].iloc[i],
                                                            line=dict(
                                                                color=colors,
                                                                width=epaisseur, dash = "dashdot"),
                                                            opacity=0.9,
                                                            layer="above",
                                                        )
            
            if dfPlotly['reason'].iloc[i] == "Buy Market Order":
                
                fig.add_annotation(x=dfPlotly.index[i], y=dfPlotly['wallet'].iloc[i],
                text="A" + str(dfPlotly['index_achat'].iloc[i]),
                font_family="Droid Serif",
                font_color="green",
                # font_size=11,
                showarrow=True,
                arrowhead=1,
                arrowwidth = 1,
                arrowcolor="green",
                ax=0,
                ay=-50,
                align='center',
                # clicktoshow='onoff',
                )
                        
            elif dfPlotly['reason'].iloc[i] == "Sell Stop Loss" and dfPlotly['wallet'].iloc[i] < dfPlotly['wallet'].iloc[i-1]:
                
                fig.add_annotation(x=dfPlotly.index[i], y=dfPlotly['wallet'].iloc[i],
                text="SL" + "<br>" + str(round(((dfPlotly['wallet'].iloc[i] / dfPlotly['wallet'].iloc[i-1])-1)*100, 2)) + "%",
                font_family="Droid Serif",
                font_color="red",
                # font_size=11,
                showarrow=True,
                arrowhead=1,
                arrowwidth = 1,
                arrowcolor="red",
                ax=0,
                ay=-50,
                align='center',
                # clicktoshow='onoff',
                )
            
            elif dfPlotly['reason'].iloc[i] == "Sell Stop Loss" and dfPlotly['wallet'].iloc[i] >= dfPlotly['wallet'].iloc[i-1]:
                
                fig.add_annotation(x=dfPlotly.index[i], y=dfPlotly['wallet'].iloc[i],
                text="SL" + "<br>" + str(round(((dfPlotly['wallet'].iloc[i] / dfPlotly['wallet'].iloc[i-1])-1)*100, 2)) + "%",
                font_family="Droid Serif",
                font_color="black",
                # font_size=11,
                showarrow=True,
                arrowhead=1,
                arrowwidth = 1,
                arrowcolor="black",
                ax=0,
                ay=-50,
                align='center',
                # clicktoshow='onoff',
                )
            
            elif dfPlotly['reason'].iloc[i] == "Sell Cond. Order" and dfPlotly['wallet'].iloc[i] < dfPlotly['wallet'].iloc[i-1]:
                
                fig.add_annotation(x=dfPlotly.index[i], y=dfPlotly['wallet'].iloc[i],
                text="V" + str(dfPlotly['index_vente'].iloc[i]) + "<br>" + str(round(((dfPlotly['wallet'].iloc[i] / dfPlotly['wallet'].iloc[i-1])-1)*100, 2)) + "%",
                font_family="Droid Serif",
                font_color="fuchsia",
                # bgcolor="snow",
                # bordercolor="snow",
                # font_size=11,
                showarrow=True,
                arrowhead=1,
                arrowwidth = 1,
                arrowcolor="fuchsia",
                ax=0,
                ay=-75,
                align='center',
                # clicktoshow='onoff',
                )
            
            elif dfPlotly['reason'].iloc[i] == "Sell Cond. Order" and dfPlotly['wallet'].iloc[i] >= dfPlotly['wallet'].iloc[i-1]:
                
                fig.add_annotation(x=dfPlotly.index[i], y=dfPlotly['wallet'].iloc[i],
                text="V" + str(dfPlotly['index_vente'].iloc[i]) + "<br>" + str(round(((dfPlotly['wallet'].iloc[i] / dfPlotly['wallet'].iloc[i-1])-1)*100, 2)) + "%",
                font_family="Droid Serif",
                font_color="black",
                # bgcolor="snow",
                # bordercolor="snow",
                # font_size=11,
                showarrow=True,
                arrowhead=1,
                arrowwidth = 1,
                arrowcolor="black",
                ax=0,
                ay=-100,
                align='center',
                # clicktoshow='onoff',
                )
            
            elif dfPlotly['reason'].iloc[i] == "Sell Take Profit":
                
                fig.add_annotation(x=dfPlotly.index[i], y=dfPlotly['wallet'].iloc[i],
                text="TP" + "<br>" + str(round(((dfPlotly['wallet'].iloc[i] / dfPlotly['wallet'].iloc[i-1])-1)*100, 2)) + "%",
                font_family="Droid Serif",
                font_color="gold",
                # bgcolor="snow",
                # bordercolor="snow",
                # font_size=11,
                showarrow=True,
                arrowhead=1,
                arrowwidth = 1,
                arrowcolor="gold",
                ax=0,
                ay=-150,
                align='center',
                # clicktoshow='onoff',
                )
                
        lst_shapes=list(ply_shapes.values())
        fig.update_layout(
            shapes=lst_shapes,
            showlegend=False,
            autosize=True,
            # width=1000,
            height=630,
            legend_title_text = "Courbes",
            # title = 'Wallet progression & Trades',
            title_font_color='tomato',
            # xaxis_tickformat = '%d.%2f %B (%a)<br>%Y' # %H~%M~%S.%2f
        )
        # fig.update_layout(legend=dict(
        #     yanchor="top",
        #     y=0.99,
        #     xanchor="left",
        #     x=0.01,
        #     bgcolor= "seashell",
        #     )
        # )
        
        # fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='whitesmoke')
        # fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='whitesmoke')
        fig.show()
        
        
        # # -- tracé du cours --
        # fig2 = go.Figure()
        # stocks = ['price']
        # # df[stocks].tail()

        # traces2 = {}
        # for i in range(0, len(stocks)):
        #     traces2['trace_' + str(i)]=go.Scatter(
        #         mode='lines',
        #         x=dfPlotly.index,
        #         y=dfPlotly[stocks[i]].values,
        #         name=stocks[i]
        #     )
        # data2=list(traces2.values())  
        # fig2=go.Figure(data2)        
        # fig2.update_layout(
        #     showlegend=False,
        #     autosize=True,
        #     # width=1000,
        #     height=600,
        #     legend_title_text = "Cours",
        #     title = 'Price progression',
        #     title_font_color='blue',
        #     # xaxis_tickformat = '%d.%2f %B (%a)<br>%Y' # %H~%M~%S.%2f
        # )
        # fig2.show()
    
            
    def plot_bar_by_month(self, dfTrades):
        sns.set_theme(rc={'figure.figsize':(11.7,8.27)})
        lastMonth = int(dfTrades.iloc[-1]['date'].month)
        lastYear = int(dfTrades.iloc[-1]['date'].year)
        dfTrades = dfTrades.set_index(dfTrades['date'])
        dfTrades.index = pd.to_datetime(dfTrades.index)
        myMonth = int(dfTrades.iloc[0]['date'].month)
        myYear = int(dfTrades.iloc[0]['date'].year)
        custom_palette = {}
        dfTemp = pd.DataFrame([])
        while myYear != lastYear or myMonth != lastMonth:
            myString = str(myYear) + "-" + str(myMonth)
            try:
                myResult = (dfTrades.loc[myString].iloc[-1]['wallet'] -
                            dfTrades.loc[myString].iloc[0]['wallet'])/dfTrades.loc[myString].iloc[0]['wallet']
            except:
                myResult = 0
            # myrow = {
            #     'date': str(datetime.date(1900, myMonth, 1).strftime('%B')),
            #     'result': round(myResult*100)
            # }
            
            myrow = pd.DataFrame([[str(datetime.date(1900, myMonth, 1).strftime('%B')), round(myResult*100)]],
                        columns=['date', 'result'] )
            dfTemp = pd.concat([dfTemp, myrow], axis=0)
            
            # dfTemp = dfTemp.append(myrow, ignore_index=True)
            if myResult >= 0:
                custom_palette[str(datetime.date(1900, myMonth, 1).strftime('%B'))] = 'g'
            else:
                custom_palette[str(datetime.date(1900, myMonth, 1).strftime('%B'))] = 'r'
            # print(myYear, myMonth, round(myResult*100, 2), "%")
            if myMonth < 12:
                myMonth += 1
            else:
                g = sns.barplot(data=dfTemp,x='date',y='result', palette=custom_palette)
                for index, row in dfTemp.iterrows():
                    if row.result >= 0:
                        g.text(row.name,row.result, str(round(row.result))+'%', color='black', ha="center", va="bottom")
                        # TEST DE DECALAGE DES POURCENTAGES...
                        # g.text(row.name,row.result, str(round(row.result))+'%', x=float(index[row]), color='black', ha="center", va="bottom")
                    else:
                        g.text(row.name,row.result, '-'+str(round(row.result))+'%', color='black', ha="center", va="top")
                g.set_title(str(myYear) + ' performance in %')
                g.set(xlabel=myYear, ylabel='performance %')
                yearResult = (dfTrades.loc[str(myYear)].iloc[-1]['wallet'] -
                            dfTrades.loc[str(myYear)].iloc[0]['wallet'])/dfTrades.loc[str(myYear)].iloc[0]['wallet']
                print("----- " + str(myYear) +" Performances: " + str(round(yearResult*100,2)) + "% -----")
                plt.show()
                dfTemp = pd.DataFrame([])
                myMonth = 1
                myYear += 1

        myString = str(lastYear) + "-" + str(lastMonth)
        try:
            myResult = (dfTrades.loc[myString].iloc[-1]['wallet'] -
                        dfTrades.loc[myString].iloc[0]['wallet'])/dfTrades.loc[myString].iloc[0]['wallet']
        except:
            myResult = 0
        g = sns.barplot(data=dfTemp,x='date',y='result', palette=custom_palette)
        for index, row in dfTemp.iterrows():
            if row.result >= 0:
                g.text(row.name,row.result, str(round(row.result))+'%', color='black', ha="center", va="bottom")
            else:
                g.text(row.name,row.result, '-'+str(round(row.result))+'%', color='black', ha="center", va="top")
        g.set_title(str(myYear) + ' performance in %')
        g.set(xlabel=myYear, ylabel='performance %')
        yearResult = (dfTrades.loc[str(myYear)].iloc[-1]['wallet'] -
                dfTrades.loc[str(myYear)].iloc[0]['wallet'])/dfTrades.loc[str(myYear)].iloc[0]['wallet']
        print("----- " + str(myYear) +" Performances: " + str(round(yearResult*100,2)) + "% -----")
        plt.show()

    def past_simulation(
            self, 
            dfTrades, 
            numberOfSimulation = 100,
            lastTrainDate = "2021-06",
            firstPlottedDate = "2021-07",
            firstSimulationDate = "2021-07-15",
            trainMultiplier = 1
        ):
        dfTrades = dfTrades.set_index(dfTrades['date'])
        dfTrades.index = pd.to_datetime(dfTrades.index)
        dfTrades['resultat'] = dfTrades['wallet'].diff()
        dfTrades['resultat%'] = dfTrades['wallet'].pct_change()
        dfTrades = dfTrades.loc[dfTrades['position']=='Sell','resultat%']
        dfTrades = dfTrades + 1

        suimulationResult = []
        trainSeries = dfTrades.loc[:lastTrainDate]
        startedPlottedDate = firstPlottedDate
        startedSimulationDate = firstSimulationDate
        commonPlot = dfTrades.copy().loc[startedPlottedDate:startedSimulationDate]
        simulatedTradesLength = len(dfTrades.loc[startedSimulationDate:])
        # for i in range(numberOfSimulation):
        #     dfTemp = dfTrades.copy().loc[startedPlottedDate:]
        #     newTrades = random.sample(list(trainSeries)*trainMultiplier, simulatedTradesLength)
        #     dfTemp.iloc[-simulatedTradesLength:] = newTrades
        #     dfTemp = dfTemp.cumprod()
        #     dfTemp.plot(figsize=(20, 10))
        #     suimulationResult.append(dfTemp.iloc[-1])

        dfTemp = dfTrades.copy().loc[startedPlottedDate:]
        dfTemp = dfTemp.cumprod()
        dfTemp.plot(figsize=(20, 10), linewidth=8)
        trueResult = dfTemp.iloc[-1]
        suimulationResult.append(trueResult)
        suimulationResult.sort()
        resultPosition = suimulationResult.index(trueResult)
        resultPlacePct = round((resultPosition/len(suimulationResult))*100,2)
        maxSimulationResult = round((max(suimulationResult)-1)*100,2)
        minSimulationResult = round((min(suimulationResult)-1)*100,2)
        avgSimulationResult = round(((sum(suimulationResult)/len(suimulationResult))-1)*100,2)
        initialStrategyResult = round((trueResult-1)*100,2)

        print("Train data informations :",len(trainSeries),"trades on period [" + str(trainSeries.index[0]) + "] -> [" +
              str(trainSeries.index[len(trainSeries)-1]) + "]")
        print("The strategy is placed at",resultPlacePct,"% of all simulations")
        print("You strategy make +",initialStrategyResult,"%")
        print("The average simulation was at +",avgSimulationResult,"%")
        print("The best simulation was at +",maxSimulationResult,"%")
        print("The worst simulation was at +",minSimulationResult,"%")
        print("--- PLOT ---") 