def str_to_hex(st):
    if st.startswith('0x') or st.startswith('0X'):
            st = st[2:]

    return int(st, 16)
            
