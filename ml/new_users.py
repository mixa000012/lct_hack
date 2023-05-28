from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler


def get_new_resc(new_user, gender, birth_date):
    # new user
    columns_to_rate = [
        "Игры",
        "Образование",
        "Пение",
        "Танцы",
        "Рисование",
        "Творчество",
        "Физическая активность",
        "Спецпроект / Московский театрал",
    ]
    new_user_df = pd.DataFrame([new_user], columns=columns_to_rate)
    new_user_df["gender"] = gender
    new_user_df["birth_date"] = birth_date
    cos_sim_df = calculate_cosine_similarity(new_user_df, pivot_df)
    gender_df, age_df = calculate_age_and_gender_scores(new_user_df, users, pivot_df)
    total_df = total_similarity(cos_sim_df, gender_df, age_df)
    result = calculate_total_similarity(total_df)

    return int(result)


def read_and_process(attend, groups, users):
    column_name_mapping = {
        "уникальный номер занятия": "unique_session_id",
        "уникальный номер группы": "unique_group_id",
        "уникальный номер участника": "unique_participant_id",
        "направление 2": "direction_2",
        "направление 3": "direction_3",
        "онлайн/офлайн": "online_offline",
        "дата занятия": "session_date",
        "время начала занятия": "session_start_time",
        "время окончания занятия": "session_end_time",
    }
    attend = attend.rename(columns=column_name_mapping)
    column_name_mapping = {
        "уникальный номер": "unique_group_id",
        "направление 1": "direction_1",
        "направление 2": "direction_2",
        "направление 3": "direction_3",
        "адрес площадки": "venue_address",
        "округ площадки": "venue_district",
        "район площадки": "venue_neighborhood",
        "расписание в активных периодах": "schedule_active_periods",
        "расписание в закрытых периодах": "schedule_closed_periods",
        "расписание в плановом периоде": "schedule_planned_period",
    }
    groups = groups.rename(columns=column_name_mapping)
    column_name_mapping = {
        "уникальный номер": "unique_participant_id",
        "дата создание личного дела": "date_of_creating_personal_file",
        "пол": "gender",
        "дата рождения": "birth_date",
        "адрес проживания": "residential_address",
    }
    users = users.rename(columns=column_name_mapping)

    return attend, groups, users


def make_ratings_df(df):
    df["score"] = 1

    scores_df = df.groupby(["unique_participant_id", "direction_1"]).sum().reset_index()
    columns_to_rate = [
        "Игры",
        "Образование",
        "Пение",
        "Танцы",
        "Рисование",
        "Творчество",
        "Физическая активность",
        "Спецпроект / Московский театрал",
    ]
    pivot_df = scores_df.pivot_table(
        index="unique_participant_id", columns=["direction_1"], values="score"
    ).reset_index()
    pivot_df = pivot_df.fillna(0)
    pivot_df = pivot_df[columns_to_rate + ["unique_participant_id"]]
    scaler = MinMaxScaler(feature_range=(0, 4))

    pivot_df[columns_to_rate] = scaler.fit_transform(pivot_df[columns_to_rate])

    return pivot_df.reset_index(drop=True).set_index("unique_participant_id")


def calculate_cosine_similarity(new_user_df, pivot_df):
    #     new_user_df = pd.DataFrame([new_user], columns=pivot_df.columns)
    columns_to_rate = [
        "Игры",
        "Образование",
        "Пение",
        "Танцы",
        "Рисование",
        "Творчество",
        "Физическая активность",
        "Спецпроект / Московский театрал",
    ]
    #     display(new_user_df)
    cos_sim = cosine_similarity(pivot_df[columns_to_rate], new_user_df[columns_to_rate])

    cos_sim_df = pd.DataFrame(
        cos_sim, index=pivot_df.unique_participant_id, columns=["cosine_similarity"]
    )

    #     sorted_sim_df = cos_sim_df.sort_values(by='cosine_similarity', ascending=False)

    return cos_sim_df


def calculate_age_and_gender_scores(new_user_df, users, pivot_df):
    #     new_user_df = pd.DataFrame([new_user], columns=pivot_df.columns)
    users["birth_date"] = pd.to_datetime(users["birth_date"])
    users["age"] = (datetime.now() - users["birth_date"]).apply(
        lambda x: int(x.days / 365.25)
    )
    new_user_df["birth_date"] = pd.to_datetime(new_user_df["birth_date"])
    new_user_df["age"] = (datetime.now() - new_user_df["birth_date"]).apply(
        lambda x: int(x.days / 365.25)
    )

    users_df = pivot_df.merge(
        users[["gender", "age", "unique_participant_id"]], on="unique_participant_id"
    )

    gender_similarity = (users_df["gender"] == new_user_df["gender"][0]).astype(int)
    gender_df = pd.DataFrame(
        {
            "unique_participant_id": users_df.unique_participant_id,
            "gen_similarity": gender_similarity,
        }
    )

    age_difference = np.abs(users_df["age"] - new_user_df["age"][0])
    age_similarity = np.exp(
        -age_difference / 10
    )  # the denominator is a tunable parameter
    age_df = pd.DataFrame(
        {
            "unique_participant_id": users_df.unique_participant_id,
            "age_similarity": age_similarity,
        }
    )

    return gender_df, age_df


def total_similarity(cos_sim_df, gender_df, age_df):
    total_sim_df = cos_sim_df.merge(gender_df, on="unique_participant_id").merge(
        age_df, on="unique_participant_id"
    )
    #     display(total_sim_df)
    #     print(0.7 * total_sim_df.cosine_similarity + 0.1 * total_sim_df.gen_similarity + 0.2 * total_sim_df.age_similaity)
    return total_sim_df


def calculate_total_similarity(total_df):
    total_df["similarity"] = (
        0.7 * total_df.cosine_similarity
        + 0.1 * total_df.gen_similarity
        + 0.2 * total_df.age_similarity
    )
    sorted_sim_df = total_df.sort_values(by="similarity", ascending=False)
    #     display(sorted_sim_df)
    return sorted_sim_df.unique_participant_id.iloc[0]


pivot_df = pd.read_csv("ml/pivot_df.csv")
users = pd.read_csv("ml/users.csv")
column_name_mapping = {
    "уникальный номер": "unique_participant_id",
    "дата создание личного дела": "date_of_creating_personal_file",
    "пол": "gender",
    "дата рождения": "birth_date",
    "адрес проживания": "residential_address",
}
users = users.rename(columns=column_name_mapping)
