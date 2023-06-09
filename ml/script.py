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
        nn_model: implicit.nearest_neighbours.CosineRecommender,
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
            return sparse.csr_matrix((data, (row_indices, col_indices)), shape=(1))

    async def get_recs(
        self,
        N,
        user_id: int | None = None,
    ) -> np.array:
        """
        user_id (int) - это id юзера, представленный в attend.csv
        user_data (pd.DataFrame) - это данные нового юзера представленные в табличке формата (group_id; quantity)
        """
        user_ind = self.encoder.get_user_dict()[user_id]

        nn_rec = self.nn_model.recommend(
            user_ind,
            self.sparse_user_group[user_ind],
            filter_already_liked_items=True,
            N=3000,
        )[0]

        als_rec = self.als_model.recommend(
            user_ind,
            self.sparse_user_group[user_ind],
            filter_already_liked_items=True,
            N=3000,
        )[0]
        als_rec = als_rec[~np.in1d(als_rec, nn_rec)]

        return [self.encoder.to_group_id(i) for i in np.concatenate([nn_rec, als_rec])][
            :N
        ]


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
    nn_model = get_model("ml/als.pkl")

    sparse_user_group = sparse.csr_matrix(
        (
            group_data["quantity"].astype(float),
            (group_data["user_id"], group_data["group_id"]),
        )
    )
    predictor_ = Predictor(
        encoder, sparse_user_group, als_model=model, nn_model=nn_model
    )
    return predictor_


predictor = get_predictor()


async def get_recs(chat_id: int, N):
    result = await predictor.get_recs(user_id=chat_id, N=N)
    return result


#
groups_metros = pd.read_csv("ml/groups_metros.csv")


async def get_final_groups(chat_id: int, metro_human=None):
    groups = await get_recs(chat_id=chat_id, N=3000)
    groups_list = groups
    groups_metros_df = pd.DataFrame({"unique_group_id": groups_list})
    groups_metros_df = groups_metros_df.merge(
        groups_metros[["id", "around_metros"]], left_on="unique_group_id", right_on="id"
    )
    online_groups = (
        groups_metros_df[groups_metros_df.around_metros == "Онлайн"]
        .unique_group_id[:10]
        .tolist()
    )
    if metro_human is not None:
        offline_groups = (
            groups_metros_df[
                (groups_metros_df.around_metros.str.contains(metro_human, case=False))
            ]
            .unique_group_id[:10]
            .tolist()
        )
    else:
        offline_groups = (
            groups_metros_df[~(groups_metros_df.around_metros == "Онлайн")]
            .unique_group_id[:10]
            .tolist()
        )

    return offline_groups[:5] + online_groups[:5]
