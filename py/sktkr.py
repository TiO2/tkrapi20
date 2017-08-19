"""
sktkr.py

This script should use sklearn to learn from stock market data.

"""

import io
import pdb
import os
import flask
import datetime      as dt
import flask_restful as fr
import numpy         as np
import pandas        as pd
import sqlalchemy    as sql
import sklearn.linear_model as skl
# modules in the py folder:
import pgdb

def learn_predict_sklinear(tkr='ABC',yrs=20,mnth='2016-11', features='pct_lag1,slope4,moy'):
  """This function should use sklearn to learn, predict."""
  linr_model = skl.LinearRegression()
  xtrain_a, ytrain_a, xtest_a, out_df = pgdb.get_train_test(tkr,yrs,mnth,features)
  if ((xtrain_a.size == 0) or (ytrain_a.size == 0) or (xtest_a.size == 0)):
    return out_df # probably empty too.
  # I should fit a model to xtrain_a, ytrain_a
  linr_model.fit(xtrain_a,ytrain_a)
  # I should predict xtest_a then update out_df
  out_df['prediction']    = np.round(linr_model.predict(xtest_a),3).tolist()
  out_df['effectiveness'] = np.sign(out_df.pct_lead*out_df.prediction)*np.abs(out_df.pct_lead)
  out_df['accuracy']      = (1+np.sign(out_df.effectiveness))/2
  algo = 'sklinear'
  pgdb.predictions2db(tkr,yrs,mnth,features,algo,out_df)
  return out_df

def learn_predict_sklinear_yr(tkr='ABC',yrs=20,yr=2016, features='pct_lag1,slope4,moy'):
  """This function should use sklearn to learn and predict for a year."""
  yr_l = []
  # I should rely on monthy predictions:
  for mnth_i in range(1,13):
    mnth_s = str(mnth_i).zfill(2)
    mnth   = str(yr)+'-'+mnth_s
    m_df   = learn_predict_sklinear(tkr,yrs,mnth, features)
    yr_l.append(m_df)
  # I should gather the monthy predictions:
  yr_df = pd.concat(yr_l, ignore_index=True)
  return yr_df

def learn_predict_sklinear_tkr(tkr='ABC',yrs=20, features='pct_lag1,slope4,moy'):
  """This function should use sklearn to learn and predict for a tkr."""
  # From db, I should get a list of all months for tkr:
  mnth_l = pgdb.getmonths4tkr(tkr)
  # I cant predict all of mnth_l. Some lack enough history.
  # I should convert yrs to months:
  month_i     = yrs * 12
  shortmnth_l = mnth_l[month_i:] # Have enough history.
  # I should rely on monthy predictions:
  tkr_l = []
  for mnth_s in shortmnth_l:
    m_df = learn_predict_sklinear(tkr,yrs,mnth_s, features)
    tkr_l.append(m_df)
  # I should gather the monthy predictions:
  tkr_df = pd.concat(tkr_l, ignore_index=True)
  return tkr_df

'bye'
