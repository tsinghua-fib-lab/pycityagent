'''空间记忆持久化'''
async def spacialPersistence(wm, sp):
    if wm.sence != None:
        sence_buffer = wm.sence
        poi_list = []
        for poi in sence_buffer['pois']:
            poi_info = poi[0]
            poi_id = poi_info['id']
            name = poi_info['name']
            category = poi_info['category']
            aoi_id = poi_info['aoi_id']
            m_p = {'id': poi_id, 'name': name, 'category': category, 'aoi_id': aoi_id, 'relation': '偶尔看到'}
            poi_list.append(m_p)
        sp.Forward(poi_list)
