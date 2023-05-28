import pickle

import implicit
import numpy as np
import pandas as pd
import scipy.sparse as sparse


class Encoder:
    def __init__(self, unique_groups: np.ndarray, unique_users: np.ndarray):
        self.group_dict = dict(
            zip(unique_groups, np.arange(unique_groups.shape[0], dtype=np.int32))
        )
        self.user_dict = dict(
            zip(unique_users, np.arange(unique_users.shape[0], dtype=np.int32))
        )

    def get_user_dict(self) -> dict:
        return self.user_dict

    def get_group_dict(self) -> dict:
        return self.group_dict

    def to_user_id(self, ind) -> str:
        for key, value in self.user_dict.items():
            if value == ind:
                return key

    def to_group_id(self, ind) -> str:
        for key, value in self.group_dict.items():
            if value == ind:
                return key


class Predictor:
    def __init__(
            self,
            encoder: Encoder,
            sparse_user_group: sparse.csr,
            als_model: implicit.als.AlternatingLeastSquares,
            nn_model: implicit.nearest_neighbours.CosineRecommender
    ) -> None:
        self.encoder = encoder
        self.model = als_model
        self.sparse_user_group = sparse_user_group
        self.nn_model = nn_model
        self.als_model = als_model

    def user_to_sparce(
            self, user_id: int | None = None, user_data: pd.DataFrame | None = None
    ) -> sparse.csr_matrix:
        """
        user_ind (int) подается, как id юзера в изначальной табличке
        user_data (pd.DataFrame) подается, если это новый пользователь, соотвественно никакого user_ind не нужно
        """
        if user_id:
            user_id = self.encoder.get_user_dict()[user_id]
            row = self.sparse_user_group.getrow(user_id)
            print(sparse.csr_matrix(row).nnz)
            return sparse.csr_matrix(row)
        elif user_data:
            user_data.group_id = user_data.group_id.apply(
                lambda x: self.encoder.get_group_dict()[x]
            )
            data = []
            row_indices = []
            col_indices = []
            for group in list(user_data.group_id.unique()):
                visit_count = user_data.loc[
                    (user_data["group_id"] == group), "quantity"
                ].values[0]
                data.append(visit_count)
                row_indices.append(0)
                col_indices.append(group)
            return sparse.csr_matrix(
                (data, (row_indices, col_indices)), shape=(1, len(unique_groups))
            )

    async def get_recs(
            self, user_id: int | None = None, user_data: pd.DataFrame | None = None
    ) -> np.array:
        """
        user_id (int) - это id юзера, представленный в attend.csv
        user_data (pd.DataFrame) - это данные нового юзера представленные в табличке формата (group_id; quantity)
        """
        user_ind = self.encoder.get_user_dict()[user_id]

        nn_rec = self.nn_model.recommend(user_ind,
                                         self.sparse_user_group[user_ind],
                                         filter_already_liked_items=True, N=60)[0]
        recs = nn_rec
        als_rec = self.als_model.recommend(user_ind,
                                           self.sparse_user_group[user_ind],
                                           filter_already_liked_items=True, N=60)[0]
        nn_rec_shape = nn_rec.shape[0]
        if nn_rec_shape < 60:
            for i in range(nn_rec_shape, 60):
                recs = np.append(recs, als_rec[i - nn_rec_shape])
        return [self.encoder.to_group_id(i) for i in recs]


def get_model(path) -> implicit.als.AlternatingLeastSquares:
    with open(path, "rb") as f:
        loaded_model = pickle.load(f)
    return loaded_model


def get_predictor():
    group_data = pd.read_csv("ml/grp.csv")
    group_data.rename(columns={"direct_2": "quantity"}, inplace=True)
    unique_groups = group_data.group_id.unique()
    unique_users = group_data.user_id.unique()

    encoder = Encoder(unique_groups, unique_users)
    user_dict = encoder.get_user_dict()
    group_dict = encoder.get_group_dict()

    group_data["user_id"] = group_data.user_id.apply(lambda i: user_dict[i])
    group_data["group_id"] = group_data.group_id.apply(lambda i: group_dict[i])

    model = get_model("ml/nearest_neighbours.pkl")
    nn_model = get_model('ml/als.pkl')

    sparse_user_group = sparse.csr_matrix(
        (
            group_data["quantity"].astype(float),
            (group_data["user_id"], group_data["group_id"]),
        )
    )
    predictor_ = Predictor(encoder, sparse_user_group, als_model=model, nn_model=nn_model)
    return predictor_


predictor = get_predictor()


async def get_recs(chat_id: int):
    result = await predictor.get_recs(chat_id)
    return result
