

class Lobby:
    def __init__(self):
        #self.lobby_name = lobby_name
        self.player_count = 0
        self.room_id = "" #for now if we change opinion
        self.players = []

    def create_lobby(self, net, packet, lobbies):
        lobby_data = packet #so this is where we recieve the room's name or packet and it's in our form
        
        self.player_count += 1#when we make a room there should be at least one that will join so we add 1 to player
        lobbies[lobby_data["MESSAGE"]] = {"player_count": self.player_count, "users": self.players, "name": lobby_data["MESSAGE"]}
        net.packet["MESSAGE"] = lobbies[lobby_data["MESSAGE"]]
        net.packet["SUCCESS"] = True
        net.packet["TYPE"] = "LOBBYINFO"
#this all means we're sending the room
        return net.packet
    
    def join_lobby(self, net, packet, lobbies):
        lobby_name = packet

        for lobby in lobbies:
            if lobby_name["MESSAGE"][0] in lobbies:
                lobbies[lobby]["player_count"] += 1
                lobbies[lobby]["users"].append(lobby_name["MESSAGE"][1])
                net.packet["MESSAGE"] = lobbies[lobby]
                net.packet["SUCCESS"] = True
                net.packet["TYPE"] = "LOBBYJOIN" 

        return net.packet

    def announce_lobby(self, net, packet, lobbies):
        for lobby in lobbies:
            net.packet["MESSAGE"] = lobbies[lobby]
            net.packet["SUCCESS"] = True
            net.packet["TYPE"] = "LOBBYINFO"
        
        return net.packet
        
            