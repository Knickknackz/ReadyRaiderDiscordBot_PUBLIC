import discord

# permissions for the bot and users PERMISSIONS INTEGER 805661936
# INVITE LINK:
# https://discord.com/api/oauth2/authorize?client_id=698180392766930996&permissions=805661936&scope=bot
#
# permissions for raid and loot channels
default_role_perms_comp_raid = discord.PermissionOverwrite(create_instant_invite=False,
                                                           manage_channels=False,
                                                           manage_roles=False,
                                                           manage_webhooks=False,
                                                           manage_messages=False,
                                                           embed_links=False,
                                                           attach_files=False,
                                                           mention_everyone=True,
                                                           external_emojis=True,
                                                           add_reactions=True,
                                                           send_messages=True,
                                                           send_tts_messages=False,
                                                           read_messages=True,
                                                           read_message_history=True)

# Bot Permissions (also RR channel permissions)
bot_perms = discord.PermissionOverwrite(create_instant_invite=False,
                                        manage_channels=True,
                                        manage_roles=True,
                                        manage_webhooks=True,
                                        manage_messages=True,
                                        embed_links=True,
                                        attach_files=True,
                                        mention_everyone=False,
                                        external_emojis=True,
                                        add_reactions=True,
                                        send_messages=True,
                                        send_tts_messages=False,
                                        read_messages=True,
                                        read_message_history=True)

#
default_role_perms_commands = discord.PermissionOverwrite(create_instant_invite=False,
                                                          manage_channels=False,
                                                          manage_roles=False,
                                                          manage_webhooks=False,
                                                          manage_messages=False,
                                                          embed_links=True,
                                                          attach_files=True,
                                                          mention_everyone=True,
                                                          external_emojis=True,
                                                          add_reactions=True,
                                                          send_messages=True,
                                                          send_tts_messages=False,
                                                          read_messages=True,
                                                          read_message_history=True)

# Bot Join Permissions
bot_join_permissions = {'add_reactions': True,
                        'administrator': False,
                        'attach_files': True,
                        'ban_members': False,
                        'change_nickname': False,
                        'connect': False,
                        'create_instant_invite': False,
                        'deafen_members': False,
                        'embed_links': True,
                        'external_emojis': True,
                        'kick_members': False,
                        'manage_channels': True,
                        'manage_emojis': False,
                        'manage_guild': True,
                        'manage_messages': True,
                        'manage_nicknames': False,
                        'manage_roles': True,
                        'manage_webhooks': False,
                        'mention_everyone': False,
                        'move_members': False,
                        'mute_members': False,
                        'priority_speaker': False,
                        'read_message_history': True,
                        'read_messages': True,
                        'send_messages': True,
                        'send_tts_messages': False,
                        'speak': False,
                        'stream': False,
                        'use_voice_activation': False,
                        'view_audit_log': True}
