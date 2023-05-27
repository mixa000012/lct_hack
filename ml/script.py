import scipy.sparse as sparse
import implicit
import pandas as pd
import numpy as np
import pickle


class Encoder:
    def __init__(self, unique_groups: np.ndarray, unique_users: np.ndarray):
        self.group_dict = dict(zip(unique_groups, np.arange(unique_groups.shape[0], dtype=np.int32)))
        self.user_dict = dict(zip(unique_users, np.arange(unique_users.shape[0], dtype=np.int32)))

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
    def __init__(self, encoder: Encoder, sparse_user_group: sparse.csr,
                 fitted_model: implicit.als.AlternatingLeastSquares, \
                 ) -> None:
        self.encoder = encoder
        self.model = fitted_model
        self.sparse_user_group = sparse_user_group

    def user_to_sparce(self, user_id: int | None = None, user_data: pd.DataFrame | None = None) -> sparse.csr_matrix:
        '''
        user_ind (int) подается, как id юзера в изначальной табличке
        user_data (pd.DataFrame) подается, если это новый пользователь, соотвественно никакого user_ind не нужно
        '''
        if user_id:
            user_id = self.encoder.get_user_dict()[user_id]
            row = self.sparse_user_group.getrow(user_id)
            print(sparse.csr_matrix(row).nnz)
            return sparse.csr_matrix(row)
        elif user_data:
            user_data.group_id = user_data.group_id.apply(lambda x: self.encoder.get_group_dict()[x])
            data = []
            row_indices = []
            col_indices = []
            for group in list(user_data.group_id.unique()):
                visit_count = user_data.loc[(user_data["group_id"] == group), "quantity"].values[0]
                data.append(visit_count)
                row_indices.append(0)
                col_indices.append(group)
            return sparse.csr_matrix((data, (row_indices, col_indices)), shape=(1, len(unique_groups)))

    async def get_recs(self, user_id: int | None = None, user_data: pd.DataFrame | None = None) -> np.array:
        '''
        user_id (int) - это id юзера, представленный в attend.csv
        user_data (pd.DataFrame) - это данные нового юзера представленные в табличке формата (group_id; quantity)
        '''
        if user_id:
            sparse_user = self.user_to_sparce(user_id)
            user_id = self.encoder.get_user_dict()[user_id]
            user_rec = self.model.recommend(user_id, user_items=sparse_user, N=10,
                                            filter_already_liked_items=False, recalculate_user=False)[0]
            return [self.encoder.to_group_id(i) for i in user_rec]
        elif user_data:
            sparse_user = self.user_to_sparce(user_data=user_data)
            user_rec = self.model.recommend(userid=0, user_items=sparse_user, N=10,
                                            filter_already_liked_items=False, recalculate_user=True)[0]
            return [self.encoder.to_group_id(i) for i in user_rec]


def get_model(path) -> implicit.als.AlternatingLeastSquares:
    with open(path, "rb") as f:
        loaded_model = pickle.load(f)
    return loaded_model


def get_predictor():

    group_data = pd.read_csv('ml/grp.csv')
    group_data.rename(columns={'direct_2': 'quantity'}, inplace=True)
    unique_groups = group_data.group_id.unique()
    unique_users = group_data.user_id.unique()

    encoder = Encoder(unique_groups, unique_users)
    user_dict = encoder.get_user_dict()
    group_dict = encoder.get_group_dict()

    group_data['user_id'] = group_data.user_id.apply(lambda i: user_dict[i])
    group_data['group_id'] = group_data.group_id.apply(lambda i: group_dict[i])

    model = get_model('ml/implicit_als_model.pkl')

    sparse_user_group = sparse.csr_matrix(
        (group_data['quantity'].astype(float), (group_data['user_id'], group_data['group_id'])))
    predictor_ = Predictor(encoder, sparse_user_group, model)
    return predictor_


predictor = get_predictor()


async def get_recs(chat_id: int):
    result = await predictor.get_recs(chat_id)
    return result
