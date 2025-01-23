import pycityproto.city.economy.v2.economy_pb2 as economyv2
from pycityagent.cityagent import SocietyAgent

async def mobility_metric(simulation):
    # 使用函数属性来存储计数
    if not hasattr(mobility_metric, 'step_count'):
        mobility_metric.step_count = 0
        
    # 统计访问地点数量
    citizen_agents = await simulation.filter(types = [SocietyAgent])
    poi_visited_info = await simulation.gather( "number_poi_visited", citizen_agents)
    poi_visited_sum = 0
    for group_gather in poi_visited_info:
        for agent_uuid, poi_visited in group_gather.items():
            poi_visited_sum += poi_visited
    average_poi_visited = float(poi_visited_sum / len(citizen_agents))
    print(f"Metric: Average POIs visited: {average_poi_visited}")
    await simulation.mlflow_client.log_metric(key="average_poi_visited", value=average_poi_visited, step=mobility_metric.step_count)
    await simulation.mlflow_client.log_metric(key="poi_visited_sum", value=poi_visited_sum, step=mobility_metric.step_count)
    mobility_metric.step_count += 1

async def economy_metric(simulation):
    # 使用函数属性来存储计数
    if not hasattr(economy_metric, 'step_count'):
        economy_metric.step_count = 0
    
    nbs_id = await simulation.economy_client.get_org_entity_ids(economyv2.ORG_TYPE_NBS)
    nbs_id = nbs_id[0]
    try:
        real_gdp = await simulation.economy_client.get(nbs_id, 'real_gdp')
    except:
        real_gdp = []
    if len(real_gdp) > 0:
        real_gdp = real_gdp[0]
        await simulation.mlflow_client.log_metric(key="real_gdp", value=real_gdp, step=economy_metric.step_count)
        other_metrics = ['prices', 'working_hours', 'depression', 'consumption_currency', 'income_currency']
        other_metrics_names = ['price', 'working_hours', 'depression', 'consumption', 'income']
        for metric, metric_name in zip(other_metrics, other_metrics_names):
            metric_value = (await simulation.economy_client.get(nbs_id, metric))[-1]
            await simulation.mlflow_client.log_metric(key=metric_name, value=metric_value, step=economy_metric.step_count)
    economy_metric.step_count += 1
