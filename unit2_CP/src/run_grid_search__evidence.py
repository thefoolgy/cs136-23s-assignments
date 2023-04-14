'''
Summary
-------
1. Select best hyperparameters (alpha, beta) of linear regression via a grid search
-- Use the evidence function of PosteriorPredictionEstimator on training set.
2. Plot the best evidence found vs. polynomial feature order.
-- Normalize scale of log probabilities by dividing by train size N
3. Report test set performance of best overall model (alpha, beta, order)
4. Report overall time required for model selection

'''

import numpy as np
import pandas as pd
import time
import os

import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")
sns.set_context("notebook")

import itertools

import regr_viz_utils
from FeatureTransformPolynomial import PolynomialFeatureTransform
from LinearRegressionPosteriorPredictiveEstimator import LinearRegressionPosteriorPredictiveEstimator

if __name__ == '__main__':
    # Load and unpack training and test data
    data_dir = os.path.abspath('../unit2_CP/data/') # FIXME if you move the data dir
    train_csv_fpath = os.path.join(data_dir, 'toywave_train.csv')
    test_csv_fpath = os.path.join(data_dir, 'toywave_test.csv')
    train_df = pd.read_csv(train_csv_fpath)
    test_df = pd.read_csv(test_csv_fpath)
    x_train_ND, t_train_N = train_df['x'].values[:,np.newaxis], train_df['y'].values
    x_test_ND, t_test_N = test_df['x'].values[:,np.newaxis], test_df['y'].values

    # Define polynomial orders to try
    order_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    # Define alpha/beta configurations to try
    # Coarse list of possible alpha
    # Finer list of possible beta (likelihoods matter more)
    params_to_search = dict(
        alpha=np.logspace(-4, 2, 7).tolist(),
        beta=np.logspace(-2, 4, 7 + 6 * 3).tolist(),
        )
    print("Possible alpha parameters")
    print(', '.join(['%.4f' % a for a in params_to_search['alpha']]))
    print("Possible beta parameters")
    print(', '.join(['%.3f' % a for a in params_to_search['beta']]))

    score_vs_N_fig = plt.figure()
    for N, line_color in [ (20, 'r'), (512, 'k')]:
        print("\n === Grid search for (alpha, beta, order) on N=%d train set" % N)
        score_per_order = list()
        estimator_per_order = list()
        start_time = time.time()
        for order in order_list:
            feature_transformer = PolynomialFeatureTransform(order=order, input_dim=1)
            param_list = list()
            score_list = list()
            estimator_list = list()
            for alpha, beta in itertools.product(
                    params_to_search['alpha'], params_to_search['beta']):
                ppe_estimator = LinearRegressionPosteriorPredictiveEstimator(
                    feature_transformer, alpha=alpha, beta=beta)
                ## TODO call fit_and_calc_log_evidence to get score for search
                score = ppe_estimator.fit_and_calc_log_evidence(x_train_ND[:N], t_train_N[:N])
                score_list.append(score)
                param_list.append(dict(alpha=alpha, beta=beta))
                estimator_list.append(ppe_estimator)

            ## Select best scoring hyperparameters
            best_id = np.argmax(score_list) # TODO identify the best scoring entry in the score list
            best_score = score_list[best_id]
            best_estimator = estimator_list[best_id]

            estimator_per_order.append(best_estimator)
            score_per_order.append(best_score)            

        if N == 20:
            ## Create Fig 3a
            key_order_list = [1, 3, 9]
            key_est_list = [estimator_per_order[oo] for oo in key_order_list]
            regr_viz_utils.make_fig_for_estimator(
                LinearRegressionPosteriorPredictiveEstimator,
                order_list=key_order_list,
                alpha_list=[est.alpha for est in key_est_list],
                beta_list=[est.beta for est in key_est_list],
                x_train_ND=x_train_ND[:N],
                t_train_N=t_train_N[:N],
                color='g',
                legend_label='PPE prediction',
                )

        ## Add line to Fig 3b
        plt.figure(score_vs_N_fig.number)
        plt.plot(order_list, score_per_order, 
            color=line_color,
            linestyle='-',
            marker='s',
            label='N=%d' % N)
        ## Add small vertical bar to indicate maximum
        vert_bar_xs = np.zeros(2)
        vert_bar_ys = np.asarray([-0.05, +0.05])
        best_id = np.argmax(score_per_order)
        plt.plot(
            vert_bar_xs + order_list[best_id],
            vert_bar_ys + score_per_order[best_id],
            linestyle='-',
            color=line_color)

        ## Report best performance of the best estimator across orders
        best_estimator_overall = estimator_per_order[best_id]

        # Summarize search
        print("Best Overall PPE at N=%d" % (N))
        print("order = %d" % order_list[best_id])
        print("alpha = %.3g" % best_estimator_overall.alpha)
        print("beta = %.3g" % best_estimator_overall.beta)
        print("test score = % 9.7f" % (
            best_estimator_overall.score(x_test_ND, t_test_N) / t_test_N.size))
        print("required time = %.2f sec" % (time.time() - start_time))

    ## Finalize figure 3b
    plt.xlabel('Polynomial Order')
    plt.ylabel('Model Evidence') 
    plt.legend(loc='upper left')
    plt.ylim([-1.4, 0.1]) # don't touch these, should be just fine
    plt.tight_layout()
    plt.show()
