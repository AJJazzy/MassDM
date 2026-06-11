with open('game/ui/hud.py', 'r') as f:
    content = f.read()

# Use actual asterisk character
corrupted = 'NO' + '*' * 8 + 'ION'
content = content.replace(corrupted + '_DURATION', 'NOTIFICATION_DURATION')
content = content.replace(corrupted + '_FONT_SIZE', 'NOTIFICATION_FONT_SIZE')

with open('game/ui/hud.py', 'w') as f:
    f.write(content)
print('Fixed hud.py')
