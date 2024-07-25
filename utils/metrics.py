import os
import numpy as np
import pandas as pd
from skimage.measure import label, regionprops


def compute_max_HD_distance(gt_shape, spacing):
    """
    Set distance metric to be the maximum value (diagonal of bounding box for the entire image).
    """
    delta_h, delta_w, delta_d = gt_shape
    max_hd_value = np.linalg.norm(
        np.array([delta_h * spacing[0], delta_w * spacing[1], delta_d * spacing[2]]))
    return max_hd_value


def compute_max_HD_distance_per_structure(seg, ind, spacing):
    """
    Set distance metric to be the maximum value (diagonal of bounding box for the target structure).
    """
    seg_binary = np.copy(seg)
    seg_binary[seg_binary != ind] = 0
    seg_binary[seg_binary == ind] = 1
    labeled_mask = label(seg_binary)
    props = regionprops(labeled_mask)
    sorted_props = sorted(props, key=lambda prop: prop.area, reverse=True)
    min_h, min_w, min_d, max_h, max_w, max_d = sorted_props[0].bbox
    delta_h = abs(max_h - min_h)
    delta_w = abs(max_w - min_w)
    delta_d = abs(max_d - min_d)
    max_hd_value = np.linalg.norm(
        np.array([delta_h * spacing[0], delta_w * spacing[1], delta_d * spacing[2]]))
    return max_hd_value


def compute_mean_per_column(matrix):
    # Convert the matrix to a NumPy array for easier manipulation
    arr = np.array(matrix).astype(float)

    # Replace the values -1 and -2 with NaN (Not a Number) to exclude them from the mean calculation
    arr[(arr == -1) | (arr == -2)] = np.nan

    # Calculate the mean per column (axis=0), ignoring NaN values
    mean_per_column = np.nanmean(arr, axis=0)

    return mean_per_column


def save_metric(gt_labelmap, ids, hd95matrix, hdmatrix, nsdmatrix, dicematrix, outputdir, datasetname, splits, part=None):
    local_ids = ids.copy()
    local_splits = splits.copy()

    columns = ['ids']
    columns.append('split')
    for name in gt_labelmap.values():
        columns.append(name)

    local_ids.append('avg')
    local_splits.append(None)
    # write dice scores to excel file
    data = {}
    avg = compute_mean_per_column(dicematrix)
    for i, col in enumerate(columns):
        if col == 'ids':
            data[col] = local_ids
        elif col == 'split':
            data[col] = local_splits
        else:
            data[col] = np.hstack([dicematrix[:, i - 2], avg[i - 2]])

    df = pd.DataFrame(data, columns=columns)
    outfolder = os.path.join(outputdir, datasetname)

    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

    if part is not None:
        filename = os.path.join(
            outfolder, f'dice_score_{datasetname}_part_{part}.xlsx')
    else:
        filename = os.path.join(outfolder, f'dice_score_{datasetname}.xlsx')
    df.to_excel(filename, index=False, header=True)

    # write hdscores to excel file
    data = {}
    avg = compute_mean_per_column(hdmatrix)
    for i, col in enumerate(columns):
        if col == 'ids':
            data[col] = local_ids
        elif col == 'split':
            data[col] = local_splits
        else:
            data[col] = np.hstack([hdmatrix[:, i - 2], avg[i - 2]])

    df = pd.DataFrame(data, columns=columns)

    if part is not None:
        filename = os.path.join(
            outfolder, f'hd_score_{datasetname}_part_{part}.xlsx')
    else:
        filename = os.path.join(outfolder, f'hd_score_{datasetname}.xlsx')

    df.to_excel(filename, index=False, header=True)

    # write hd95 to excel file
    data = {}
    avg = compute_mean_per_column(hd95matrix)
    for i, col in enumerate(columns):
        if col == 'ids':
            data[col] = local_ids
        elif col == 'split':
            data[col] = local_splits
        else:
            data[col] = np.hstack([hd95matrix[:, i - 2], avg[i - 2]])

    df = pd.DataFrame(data, columns=columns)

    if part is not None:
        filename = os.path.join(
            outfolder, f'hd95_score_{datasetname}_part_{part}.xlsx')
    else:
        filename = os.path.join(outfolder, f'hd95_score_{datasetname}.xlsx')

    df.to_excel(filename, index=False, header=True)

    # write normalizes surface distance to excel file
    data = {}
    avg = compute_mean_per_column(nsdmatrix)
    for i, col in enumerate(columns):
        if col == 'ids':
            data[col] = local_ids
        elif col == 'split':
            data[col] = local_splits
        else:
            data[col] = np.hstack([nsdmatrix[:, i - 2], avg[i - 2]])

    df = pd.DataFrame(data, columns=columns)

    if part is not None:
        filename = os.path.join(
            outfolder, f'normalized_distance_{datasetname}_part_{part}.xlsx')
    else:
        filename = os.path.join(
            outfolder, f'normalized_distance_{datasetname}.xlsx')

    df.to_excel(filename, index=False, header=True)

    if part is not None:
        filename = os.path.join(
            outfolder, f'metrics_{datasetname}_part_{part}.npz')
    else:
        filename = os.path.join(outfolder, f'metrics_{datasetname}.npz')

    np.savez(filename, dice=dicematrix, hd95=hd95matrix,
             hd=hdmatrix, nsd=nsdmatrix, splits=local_splits)


def save_missing_structure_check(count, output_folder, datasetname):
    rows = []
    for case in count.keys():
        if len(count[case]) == 0:
            continue
        else:
            for structure in count[case].keys():
                if len(count[case][structure]) == 0:
                    continue
                else:
                    for item in count[case][structure]:
                        rows.append(
                            [datasetname, case, structure, item])

    fields = ["dataset", "category", "structure", "case"]
    df = pd.DataFrame(rows, columns=fields)
    csv_file = os.path.join(
        output_folder, f"missing_structure.csv")
    if os.path.isfile(csv_file):
        df.to_csv(csv_file, mode="a", header=False)
    else:
        df.to_csv(csv_file, mode="a")
