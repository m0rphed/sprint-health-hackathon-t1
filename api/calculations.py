import os
import ast
import pandas as pd
from dataclasses import dataclass
from rich import print as print_rich
from config import (
    DATA_DIR_RAW,
    ENTITIES_FILENAME,
    HISTORY_FILENAME,
    SPRINTS_FILENAME
)

@dataclass()
class DatasetConfig:
    path_entities: str
    path_history: str
    path_sprints: str


def _read_to_df(full_path: str) -> pd.DataFrame:
    return pd.read_csv(
        full_path,
        skiprows=1,
        sep=";",
        # пустые строки будут добавлены как null-значения
        na_values=["", "<empty>"],
        keep_default_na=True,
    )


def remove_full_duplicates(
    df_name: str, df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.Series]:
    count = int(df.duplicated().sum())
    print_rich(
        f"Всего в '[italic yellow]{df_name}[/italic yellow]' полных дубликатов: [red]{count}[/red]"
    )
    return df.drop_duplicates(), df.duplicated()


def remove_empty_rows(df_name: str, df: pd.DataFrame) -> tuple[pd.DataFrame]:
    count = int(df.isna().all(axis=1).sum())
    print_rich(
        f"Всего в '[italic yellow]{df_name}[/italic yellow]' удалено полных пропусков: [red]{count}[/red]"
    )
    return df.dropna(how="all")


def clean_up_tables(config: DatasetConfig) -> dict[str, pd.DataFrame]:
    # загрузка данных из CSV файлов
    entities_df = _read_to_df(config.path_entities)
    history_df = _read_to_df(config.path_history)
    sprints_df = _read_to_df(config.path_sprints)

    tables: dict[str, pd.DataFrame] = {
        "задачи": entities_df,
        "история": history_df,
        "спринты": sprints_df,
    }

    # сохраняем дубликаты просто на всякий случай (они скорее всего не понадобятся)
    duplicates: dict[str, pd.Series] = {}
    tables_cleaned: dict[str, pd.DataFrame] = {}

    for name, df in tables.items():
        cleaned_df, duplicates = remove_full_duplicates(name, df)
        duplicates[name] = duplicates
        tables_cleaned[name] = cleaned_df

    for name, df in tables.items():
        dups_were = tables[name].duplicated().sum()
        dups_now = tables_cleaned[name].duplicated().sum()
        print(f"'{name}' было: {dups_were} - стало: {dups_now}")

    for name, df in tables_cleaned.items():
        cleaned_df = remove_empty_rows(name, df)
        tables_cleaned[name] = cleaned_df

    return tables_cleaned


def get_full_merged_df(tables_cleaned: dict[str, pd.DataFrame]) -> pd.DataFrame:
    sprints_df = tables_cleaned["спринты"]
    entities_df = tables_cleaned["задачи"]
    history_df = tables_cleaned["история"]

    # преобразование entity_ids из строки в set
    sprints_df["entity_ids"] = sprints_df["entity_ids"].apply(
        lambda x: set(ast.literal_eval(x))
    )
    # создание таблицы для связи задач со спринтами
    sprint_tasks = []
    for _, row in sprints_df.iterrows():
        sprint_id = row["sprint_name"]
        for task_id in row["entity_ids"]:
            sprint_tasks.append({"sprint_name": sprint_id, "task_id": task_id})

    sprint_tasks_df = pd.DataFrame(sprint_tasks)
    # объединение таблиц спринтов и задач
    tasks_with_sprints_df = pd.merge(
        sprint_tasks_df,
        entities_df,
        left_on="task_id",
        right_on="entity_id",
        how="left",
    )
    # объединение с таблицей истории выполнения
    full_merged_df = pd.merge(
        tasks_with_sprints_df,
        history_df,
        left_on="task_id",
        right_on="entity_id",
        how="left",
    )
    return full_merged_df


def calculate_to_do_metric(full_merged_df: pd.DataFrame) -> pd.DataFrame:
    # фильтрация задач, находящихся в статусе "Создано" на конец спринта
    latest_status_df = (
        full_merged_df.sort_values(by=["history_date", "history_version"])
        .groupby("task_id")
        .tail(1)
    )
    to_do_tasks_df = latest_status_df[
        (latest_status_df["status"] == "Создано")
        & (latest_status_df["sprint_name"].notna())
    ]

    # расчет метрики "К выполнению" для каждого спринта
    to_do_metric = to_do_tasks_df.groupby("sprint_name")["estimation"].sum() / 3600

    to_do_metric_df = to_do_metric.reset_index()
    to_do_metric_df.columns = ["Sprint Name", "To Do Metric (hours)"]
    return to_do_metric_df


if __name__ == "__main__":
    # необработанные данные ровно в таком виде как были предоставлены
    raw_data = DatasetConfig(
        path_entities=os.path.join(DATA_DIR_RAW, ENTITIES_FILENAME),
        path_history=os.path.join(DATA_DIR_RAW, HISTORY_FILENAME),
        path_sprints=os.path.join(DATA_DIR_RAW, SPRINTS_FILENAME),
    )

    tables_cleaned = clean_up_tables(raw_data)
    full_merged_df = get_full_merged_df(tables_cleaned)

    # Вычисление метрики "К выполнению"
    to_do_metric_df = calculate_to_do_metric(full_merged_df)

    # Сохранение результатов в CSV файл
    to_do_metric_df.to_csv("./to_do_metric_per_sprint.csv", index=False)

    print(
        "Метрика 'К выполнению' успешно сохранена в файл 'to_do_metric_per_sprint.csv'"
    )
