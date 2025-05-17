import IdentityManager from "@arcgis/core/identity/IdentityManager";
import OAuthInfo from "@arcgis/core/identity/OAuthInfo";


const oauthInfo = new OAuthInfo({
    appId: "bF0Vj7tJiGzVrnlq",
    popup: true,
    portalUrl: "https://portal.wsrl.nl/portal",
    popupCallbackUrl: `http://localhost:3001/oath-callback.html`,
});

// IdentityManager.registerOAuthInfos([oauthInfo]);

export async function signIn() {
    try {
        IdentityManager.registerOAuthInfos([oauthInfo]);
    } catch (e) {
        console.log(e,"error")
    }

    

}