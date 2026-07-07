# Stage 10.2 failure-boundary report

Stage 10.2 is a named-baseline benchmark, not a new biological demonstration. It tests whether RhoDyn's declared method object remains informative when compared with simple summaries and named external-style comparator families on shared inputs.

Status. `pass`.

## Main boundary

The benchmark is deliberately allowed to show that generic feature methods perform well in some regimes. That outcome does not weaken the method object by itself. It defines where classification-like summaries may be sufficient and where the RhoDyn residence decision remains more interpretable.

## Synthetic accuracy summary

| method family | method | accuracy |
| --- | --- | --- |
| catch22_feature_family | catch22_style_feature_screen | 36/36 |
| hmmlearn_gaussian_hmm_family | hmmlearn.GaussianHMM | 24/36 |
| internal_simple_summary | endpoint_value | 12/36 |
| internal_simple_summary | latency_to_peak | 18/36 |
| internal_simple_summary | mean_activity_auc | 12/36 |
| internal_simple_summary | peak_amplitude | 24/36 |
| internal_simple_summary | threshold_occupancy | 12/36 |
| rhodyn_method_object | RhoDyn_method_object | 36/36 |
| rocket_interval_kernel_family | MiniROCKET_style_interval_kernels | 24/36 |
| ruptures_changepoint_family | ruptures_style_single_changepoint | 12/36 |
| scikit_learn_feature_classifier | sklearn.RandomForestClassifier_LOOCV | 36/36 |
| scipy_signal_peak_detection | scipy.signal.find_peaks | 12/36 |
| tsfresh_feature_family | tsfresh_style_selected_features | 24/36 |

## Interpretation limits

- Synthetic known-truth rows test method behavior and comparator behavior. They are not biological evidence.
- Public DRG calcium and ERK GPCR rows compare high-scoring trace sets across methods. They do not provide ground-truth labels for superiority.
- Compatibility implementations for catch22, tsfresh, MiniROCKET, and ruptures-style families are named-family comparators when the direct package is not installed. Direct package availability is reported separately.
- A named baseline matching or beating RhoDyn in an amplitude-sufficient regime is a boundary, not a defect.
