import hvac
import pandas as pd
import json
import os
import time
from dotenv import load_dotenv

start_time = time.time()

# Load environment variables
load_dotenv()
VAULT_ADDR = os.getenv("VAULT_ADDR_PROD")
VAULT_TOKEN = os.getenv("VAULT_TOKEN_PROD")

# Load the Excel file
file_path = "vault_input_prod.xlsx"
df = pd.read_excel(file_path)

# Initialize Vault client
client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

# Output storage
output_data_create = []
output_data_regen = []
processed_count = 0

# Process each row in the Excel file
for index, row in df.iterrows():
    print(index)
    if row["status"] == "DONE":
        print("this row is skipped because the request is " + str(row["status"]).lower())
        continue
    elif row["status"] == "TODO":
        aplikasi = row["aplikasi"].strip()
        print("aplikasi:",aplikasi)
        namespace = row["namespace"]
        print("namespace:", namespace)
        mount = row["mount"].strip()
        print("mount:", mount)
        approle = "approle-" + row["approle"].strip()
        print("approle:", approle)
        policy = row["policy"].strip() + "-policy"
        print("policy:", policy)
        secret_path = row["secret"].strip()
        print("secret_path:", secret_path)

        client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN, namespace=namespace)

        try:
            secret_data = json.loads(row["keys"])  # Expecting a single JSON object now
            if not isinstance(secret_data, dict):
                print(f"Invalid JSON format in row {row}")
                continue
        except json.JSONDecodeError:
            print(f"Invalid JSON in row {row}")
            continue
        print("secret_data:", secret_data)

        # Enable secrets engine only if it doesn't exist
        existing_mounts = client.sys.list_mounted_secrets_engines()["data"].keys()
        print("existing_mounts:", existing_mounts)
        if f"{mount}/" not in existing_mounts:
            client.sys.enable_secrets_engine(backend_type="kv", path=mount, options={"version": 2})
            time.sleep(2)

        # Store secret data
        client.secrets.kv.v2.create_or_update_secret(mount_point=mount, path=secret_path, secret=secret_data)

        # Create policy
        policy_hcl = f"""
        path "{mount}/*" {{
          capabilities = ["read", "list"]
        }}
        """
        client.sys.create_or_update_policy(name=policy, policy=policy_hcl)

        client.auth.approle.create_or_update_approle(
            role_name=approle,
            token_policies=[policy],
            token_ttl="0",  
            token_max_ttl="0", 
            secret_id_ttl="0", 
            secret_id_num_uses="0"
        )

        role_id = client.auth.approle.read_role_id(role_name=approle)["data"]["role_id"]
        secret_id = client.auth.approle.generate_secret_id(role_name=approle)["data"]["secret_id"]
        print(f"Created role_id: {role_id}, secret_id: {secret_id}")

        key_list = "\n".join([f"{i+1}. {key}" for i, key in enumerate(secret_data.keys())])
        print("key_list:", key_list)

        # output_data.append([aplikasi, VAULT_ADDR, namespace, mount, secret_path, role_id, secret_id, key_list])
        output_data_create.append([aplikasi, key_list, VAULT_ADDR, namespace, secret_path, role_id, mount, secret_id])
        print("output_data_create:", output_data_create)

        # **Update status in DataFrame**
        df.at[index, "status"] = "DONE"
        processed_count+=1
        
        # Save the updated input file with new status
        df.to_excel(file_path, index=False)
        print("Updated input file with 'DONE' status.")
    elif row["status"] == "REGEN":
        aplikasi = row["aplikasi"].strip()
        print("aplikasi:",aplikasi)
        namespace = row["namespace"]
        print("namespace:", namespace)
        approle = "approle-" + row["approle"].strip()
        print("approle:", approle)
        policy = row["policy"].strip() + "-policy"
        print("policy:", policy)

        client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN, namespace=namespace)

        client.auth.approle.create_or_update_approle(
            role_name=approle,
            token_policies=[policy],
            token_ttl="0",  
            token_max_ttl="0", 
            secret_id_ttl="0", 
            secret_id_num_uses="0",
            
        )

        role_id = client.auth.approle.read_role_id(role_name=approle)["data"]["role_id"]
        secret_id = client.auth.approle.generate_secret_id(role_name=approle)["data"]["secret_id"]
        print(f"Created role_id: {role_id}, secret_id: {secret_id}")

        output_data_regen.append([aplikasi, VAULT_ADDR, namespace, role_id, secret_id])
        print("output_data_regen:", output_data_regen)

        df.at[index, "status"] = "DONE"
        processed_count+=1
        
        df.to_excel(file_path, index=False)


# Save the output to a new Excel file
    # output_df = pd.DataFrame(output_data, columns=["Application", "URL", "Namespace", "Mount", "Secret Path", "Role ID", "Secret ID", "Keys"])
output_df_create = pd.DataFrame(output_data_create, columns=["Application", "Keys", "URL", "Namespace", "Secret Path", "Role ID", "Mount", "Secret ID"])
output_df_regen = pd.DataFrame(output_data_regen, columns=["Application", "URL", "Namespace", "Role ID", "Secret ID"])

with pd.ExcelWriter("vault_output_prod.xlsx", engine="xlsxwriter") as writer:
    output_df_create.to_excel(writer, sheet_name="created", index=False)
    output_df_regen.to_excel(writer, sheet_name="regenerated", index=False)

end_time=time.time()
elapsed_time = end_time-start_time

print("Vault production setup completed successfully!")
print(f"Processed {processed_count} rows in {elapsed_time:.2f} seconds.")
