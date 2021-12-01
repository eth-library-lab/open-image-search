def clean_eth_metadata(df):
    
    # change url to lower resolution request (350x350px)
    if 'image_url' in df.columns:
        df['image_url'] = df['image_url'].str.replace('resolution=superImageResolution','resolution=highImageResolution')

    return df